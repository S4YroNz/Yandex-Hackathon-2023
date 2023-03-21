from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class CreateQuizForm(FlaskForm):
    pass
    submit = SubmitField('Создать')
