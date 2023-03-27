import os
import json
from flask import Flask, render_template, redirect, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api

from forms.user import *
from forms.quiz import QuizForm
from data import db_session, quizzes_resources
from data.users import User
from data.quizzes import Quiz

# Flask app initializing
app = Flask(__name__)
app.config['SECRET_KEY'] = '908jyuh0j67f453v5439hj78y0yvcrt9ew80ny'
api = Api(app)

# LoginManager initializing
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    # отображаем все доступные квизы ( по сколько-то на страничу, потом догружаем)
    # по хорошему нужны:
    # поиск
    # раделение по жанрам
    # навигация
    # фильтр по дате создания, чтобы новые чекать.
    db_sess = db_session.create_session()
    quizzes = db_sess.query(Quiz).all()
    return render_template('index.html', quizzes=quizzes)


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('signup.html',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.username == form.username.data).first():
            return render_template('signup.html',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            username=form.username.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/signin')
    return render_template('signup.html', form=form, message="")


@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template('signin.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('signin.html', form=form, message="")


@app.route('/signout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/quiz',  methods=['GET', 'POST'])
@login_required
def create_quiz():
    form = QuizForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        quiz = Quiz()
        quiz.creator = current_user.id
        quiz.type = form.type.data
        quiz.title = form.quiz_title.data
        quiz.description = form.description.data

        # каким-то макаром парсим все наши вопросы и персонажей
        quiz_json = {
            'characters': [field.data for field in form.characters],
            'questions': []
        }
        for formfield in form.questions:
            question_json = {
                'title': formfield.question.data,
                'answers': []
            }
            for field in formfield.answers:
                answer_json = {
                    'title': field.answer.data,
                    'characters': field.characters.data  # проверить
                }
                question_json['answers'].append(answer_json)
            quiz_json['questions'].append(question_json)

        name_file = f'/quizzes/quiz_data{quiz.id}_{quiz.title}' # формируем на основе id название json-файла
        # запихиваем туда спарсенные вопросы
        with open(name_file, 'w') as file:
            json.dump(quiz_json, file)
        quiz.content_file = name_file

        current_user.quizzes.append(quiz)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('createquiz.html', title='Добавление квиза',
                           form=form)


@app.route('/quiz/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(id):
    form = QuizForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        quiz = db_sess.query(Quiz).filter(Quiz.id == id,
                                          Quiz.user == current_user  # or Quiz.creator???
                                          ).first()
        if quiz:
            # переносим все данные квиза в соответствующие поля
            # + берем из json
            form.type.data = quiz.type
            form.title.data = quiz.title
            form.description.data = quiz.description
            name_file = quiz.content_file
            with open(name_file, 'w') as file:
                quiz_json = json.load(file)
            # берем json файл и каким то макаром переносим список персонажей
            # и каждый вопрос в свой блок

        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        quiz = db_sess.query(Quiz).filter(Quiz.id == id,
                                          Quiz.user == current_user
                                          ).first()
        if quiz:
            quiz.type = form.type.data
            quiz.title = form.title.data
            quiz.description = form.description.data
            # каким-то макаром парсим все наши вопросы и персонажей
            quiz_json = {
                'characters': [field.data for field in form.characters],
                'questions': []
            }
            for formfield in form.questions:
                question_json = {
                    'question': formfield.question.data,
                    'answers': []
                }
                for field in formfield.answers:
                    answer_json = {
                        'answer': field.answer.data,
                        'characters': field.characters.data  # проверить получаются ли так нужные данные списком
                    }
                    question_json['answers'].append(answer_json)
                quiz_json['questions'].append(question_json)

            name_file = quiz.content_file
            with open(name_file, 'w') as file:
                json.dump(quiz_json, file)  # перезаписываем json

            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('createquiz.html',
                           title='Редактирование квиза',
                           form=form
                           )


@app.route('/delete_quiz/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_quiz(id):
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == id,
                                      Quiz.user == current_user
                                      ).first()
    if quiz:
        os.remove(f'/путь/{quiz.content_file}')  # дописать путь
        db_sess.delete(quiz)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init('db/ya_quiz.db')
    api.add_resource(quizzes_resources.QuizResource, "/api/quiz")
    api.add_resource(quizzes_resources.QuizListResource, "/api/quiz/<int:quiz_id>")
    app.run(port=8080, host='127.0.0.1')

# TODO: база данных аккаунтов вида
# [id(key, int), username(str, включить индексацию), hashed_password(str),
# ownedQuizes(str тут будут id quiz'ов через пробел)]


if __name__ == "__main__":
    main()
