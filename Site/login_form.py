from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])  # добавить проверку на наличие в бд
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Регистрация/Вход')
