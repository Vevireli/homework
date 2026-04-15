from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Article, Comment, SavedArticle, SiteSettings
from forms import LoginForm, RegistrationForm, CommentForm
from utils import admin_required, calculate_ban_until
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---- Инициализация БД и создание администратора по умолчанию ----
with app.app_context():
    db.create_all()
    # Создаём администратора, если нет ни одного пользователя
    if User.query.count() == 0:
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            is_admin=True,
            is_banned=False
        )
        db.session.add(admin)
        db.session.commit()
    # Создаём настройки сайта, если нет
    if SiteSettings.query.count() == 0:
        settings = SiteSettings(bg_color='#ffffff', font_color='#000000', font_size='16px')
        db.session.add(settings)
        db.session.commit()

# ---- Контекстный процессор для настроек темы ----
@app.context_processor
def inject_settings():
    settings = SiteSettings.query.first()
    return dict(settings=settings)

# ---- Публичные маршруты (разделы города) ----
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news/')
@app.route('/news/<path:subpath>')
def news(subpath=None):
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('news.html', articles=articles)

@app.route('/news/<int:article_id>')
def news_detail(article_id):
    article = Article.query.get_or_404(article_id)
    # Увеличиваем счётчик просмотров
    article.views += 1
    db.session.commit()
    form = CommentForm()
    comments = Comment.query.filter_by(article_id=article.id).order_by(Comment.created_at.desc()).all()
    return render_template('news_detail.html', article=article, comments=comments, form=form)

@app.route('/news/<int:article_id>/comment', methods=['POST'])
@login_required
def add_comment(article_id):
    if not current_user.is_active():
        flash('Ваш аккаунт заблокирован, вы не можете комментировать.', 'danger')
        return redirect(url_for('news_detail', article_id=article_id))
    article = Article.query.get_or_404(article_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(text=form.text.data, user_id=current_user.id, article_id=article.id)
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен.', 'success')
    return redirect(url_for('news_detail', article_id=article_id))

@app.route('/save/<int:article_id>')
@login_required
def save_article(article_id):
    if not current_user.is_active():
        flash('Вы забанены.', 'danger')
        return redirect(url_for('news_detail', article_id=article_id))
    existing = SavedArticle.query.filter_by(user_id=current_user.id, article_id=article_id).first()
    if not existing:
        save = SavedArticle(user_id=current_user.id, article_id=article_id)
        article = Article.query.get(article_id)
        article.saves += 1
        db.session.add(save)
        db.session.commit()
        flash('Статья сохранена.', 'success')
    else:
        flash('Вы уже сохранили эту статью.', 'info')
    return redirect(url_for('news_detail', article_id=article_id))

# ---- Другие статические разделы (городские) ----
@app.route('/management/')
@app.route('/management/<path:subpath>')
def management(subpath=None):
    return render_template('management.html')

@app.route('/facts/')
@app.route('/facts/<path:subpath>')
def facts(subpath=None):
    return render_template('facts.html')

@app.route('/contacts/')
@app.route('/contacts/<path:subpath>')
def contacts(subpath=None):
    return render_template('contacts.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/history/people')
def history_people():
    return render_template('history_people.html')

@app.route('/history/photos')
def history_photos():
    return render_template('history_photos.html')

# ---- Аутентификация ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if user.is_active():
                login_user(user)
                flash('Вход выполнен.', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Ваш аккаунт заблокирован.', 'danger')
        else:
            flash('Неверное имя или пароль.', 'danger')
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна, теперь войдите.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли.', 'info')
    return redirect(url_for('index'))

# ---- Импорт административных маршрутов (определены в admin.py) ----
from admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)