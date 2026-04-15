from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Article, Comment, SavedArticle, SiteSettings
from forms import ArticleForm, BanForm, SettingsForm
from utils import admin_required, calculate_ban_until
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    user_count = User.query.count()
    article_count = Article.query.count()
    comment_count = Comment.query.count()
    return render_template('admin/dashboard.html',
                           user_count=user_count,
                           article_count=article_count,
                           comment_count=comment_count)

# ---- Управление пользователями ----
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_admin = 'is_admin' in request.form
        user = User(username=username, email=email,
                    password=generate_password_hash(password),
                    is_admin=is_admin)
        db.session.add(user)
        db.session.commit()
        flash('Пользователь добавлен.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/add_user.html')

@admin_bp.route('/users/delete/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Нельзя удалить самого себя.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь удалён.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/ban/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def ban_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Нельзя забанить самого себя.', 'danger')
        return redirect(url_for('admin.users'))
    form = BanForm()
    if form.validate_on_submit():
        user.is_banned = True
        user.ban_until = calculate_ban_until(form.duration.data)
        db.session.commit()
        flash(f'Пользователь {user.username} забанен.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/ban_user.html', form=form, user=user)

# ---- Управление статьями ----
@admin_bp.route('/articles')
@login_required
@admin_required
def articles():
    all_articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('admin/articles.html', articles=all_articles)

@admin_bp.route('/articles/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_article():
    form = ArticleForm()
    if form.validate_on_submit():
        article = Article(title=form.title.data, content=form.content.data, author_id=current_user.id)
        db.session.add(article)
        db.session.commit()
        flash('Статья опубликована.', 'success')
        return redirect(url_for('admin.articles'))
    return render_template('admin/edit_article.html', form=form, title='Новая статья')

@admin_bp.route('/articles/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    form = ArticleForm(obj=article)
    if form.validate_on_submit():
        article.title = form.title.data
        article.content = form.content.data
        db.session.commit()
        flash('Статья обновлена.', 'success')
        return redirect(url_for('admin.articles'))
    return render_template('admin/edit_article.html', form=form, title='Редактирование статьи')

@admin_bp.route('/articles/delete/<int:article_id>')
@login_required
@admin_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash('Статья удалена.', 'success')
    return redirect(url_for('admin.articles'))

# ---- Управление комментариями ----
@admin_bp.route('/comments')
@login_required
@admin_required
def comments():
    all_comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return render_template('admin/comments.html', comments=all_comments)

@admin_bp.route('/comments/delete/<int:comment_id>')
@login_required
@admin_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Комментарий удалён.', 'success')
    return redirect(url_for('admin.comments'))

# ---- Настройки темы ----
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    settings = SiteSettings.query.first()
    form = SettingsForm(obj=settings)
    if form.validate_on_submit():
        settings.bg_color = form.bg_color.data
        settings.font_color = form.font_color.data
        settings.font_size = form.font_size.data
        db.session.commit()
        flash('Настройки сохранены.', 'success')
        return redirect(url_for('admin.settings'))
    return render_template('admin/settings.html', form=form)

# ---- Статистика ----
@admin_bp.route('/statistics')
@login_required
@admin_required
def statistics():
    # Рейтинг статей по просмотрам
    top_views = Article.query.order_by(Article.views.desc()).limit(10).all()
    # Рейтинг по комментариям
    articles_with_comment_count = []
    for article in Article.query.all():
        cnt = Comment.query.filter_by(article_id=article.id).count()
        articles_with_comment_count.append((article, cnt))
    top_comments = sorted(articles_with_comment_count, key=lambda x: x[1], reverse=True)[:10]
    # Рейтинг по сохранениям
    top_saves = Article.query.order_by(Article.saves.desc()).limit(10).all()
    return render_template('admin/statistics.html',
                           top_views=top_views,
                           top_comments=top_comments,
                           top_saves=top_saves)