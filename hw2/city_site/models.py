from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    ban_until = db.Column(db.DateTime, nullable=True)  # None = навсегда или не забанен
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_active(self):
        if not self.is_banned:
            return True
        if self.ban_until is None:
            return False  # забанен навсегда
        return datetime.utcnow() < self.ban_until

    def get_ban_duration_display(self):
        if not self.is_banned:
            return "Не забанен"
        if self.ban_until is None:
            return "Навсегда"
        delta = self.ban_until - datetime.utcnow()
        days = delta.days
        if days <= 1:
            return "День"
        elif days <= 7:
            return "Неделя"
        elif days <= 30:
            return "Месяц"
        else:
            return "Навсегда"

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    saves = db.Column(db.Integer, default=0)  # количество сохранений
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref='articles')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    user = db.relationship('User', backref='comments')
    article = db.relationship('Article', backref='comments')

class SavedArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'article_id', name='unique_save'),)

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bg_color = db.Column(db.String(20), default='#ffffff')
    font_color = db.Column(db.String(20), default='#000000')
    font_size = db.Column(db.String(10), default='16px')