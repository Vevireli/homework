from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя уже занято.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован.')

class ArticleForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])

class CommentForm(FlaskForm):
    text = TextAreaField('Комментарий', validators=[DataRequired()])

class BanForm(FlaskForm):
    duration = SelectField('Срок бана', choices=[
        ('day', 'День'),
        ('week', 'Неделя'),
        ('month', 'Месяц'),
        ('forever', 'Навсегда')
    ], validators=[DataRequired()])

class SettingsForm(FlaskForm):
    bg_color = StringField('Цвет фона (HEX)', validators=[DataRequired()])
    font_color = StringField('Цвет шрифта (HEX)', validators=[DataRequired()])
    font_size = StringField('Размер шрифта (px, em)', validators=[DataRequired()])