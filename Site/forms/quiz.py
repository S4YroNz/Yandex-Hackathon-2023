from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms import SelectMultipleField, FieldList, Field, FormField, Form
from wtforms.fields.html5 import EmailField, TelField, SearchField, URLField
from wtforms.validators import DataRequired


class AnswerForm(Form):
    answer = StringField('Ответ', validators=[DataRequired()]) # или лучше TextArea?
    character = SelectMultipleField('Персонажи', choices=[], validators=[
        DataRequired()])  # значения для параметра choise берем из QuizForm.characters
    # добавить возможность прикреплять файлы


class QuestionForm(Form):
    question = TextAreaField('Вопрос', validators=[DataRequired()])
    answers = FieldList(FormField(AnswerForm))


class QuizForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    type = BooleanField('Тип теста', validators=[DataRequired()])
    description = TextAreaField('Описание теста', validators=[DataRequired()])

    # ?????????????
    characters = FieldList(StringField('персонаж'))
    questions = FieldList(FormField(QuestionForm))

    submit = SubmitField('Создать')
