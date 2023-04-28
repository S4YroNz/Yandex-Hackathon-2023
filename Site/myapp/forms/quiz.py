from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms import SelectMultipleField, FieldList, Field, FormField, Form, FileField
from wtforms.fields import EmailField, TelField, SearchField, URLField
from wtforms.validators import DataRequired


class CharacterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    photo = FileField('Изображение')  # добавить проверку на разширение, размер


class AnswerForm(Form):
    answer = StringField('Ответ', validators=[DataRequired()]) # или лучше TextArea?
    character = SelectMultipleField('Персонажи', choices=[], validators=[
        DataRequired()])  # значения для параметра choise берем из QuizForm.characters
    # добавить возможность прикреплять файлы


class QuestionForm(Form):
    question = TextAreaField('Вопрос', validators=[DataRequired()])
    answers = FieldList(FormField(AnswerForm))


class QuizForm(FlaskForm):
    quiz_title = StringField('Название', validators=[DataRequired()])
    quiz_preview = FileField("Заставка теста")  # + фото
    quiz_type = BooleanField('Тип теста', validators=[DataRequired()])
    description = TextAreaField('Описание теста', validators=[DataRequired()])

    characters = FieldList(StringField('персонаж'))
    questions = FieldList(FormField(QuestionForm, separator='-'))

    submit = SubmitField('Создать')
