import os
import json
from flask import Flask, render_template, redirect, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
import requests
import logging
from io import BytesIO
from werkzeug.datastructures import ImmutableMultiDict, FileStorage

from forms.user import *
from forms.quiz import QuizForm
from data import db_session, quizzes_resources
from data.users import User
from data.quizzes import Quiz
from imageResize import resize

# Flask app initializing
app = Flask(__name__)
app.config['SECRET_KEY'] = '908jyuh0j67f453v5439hj78y0yvcrt9ew80ny'
api = Api(app)

logging.basicConfig(level=logging.INFO)

# LoginManager initializing
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


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
        user = db_sess.query(User).filter(
            User.username == form.username.data).first()
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


def get_image(files: ImmutableMultiDict[FileStorage], name: str):
    print(files[name].filename)
    if files[name].filename == '':
        return
    return BytesIO(files[name].read())

@app.route('/createquiz',  methods=('GET', 'POST'))
@login_required
def create_quiz():
    quiz = {}
    if request.method == 'POST':
        form = request.form
        files = request.files
        quiz = {
            'title': form.get('quiz_title', None),
            'description': form.get('quiz_description', None),
            'creator': current_user.username,
            'image': get_image(files, 'quiz_preview'),
            'type': form.get('quiz_type', None)
        }

        if quiz['type'] == 'person':
            collect_personQuiz_data(form, files, quiz)
        else:
            collect_percentQuiz_data(form, files, quiz)

        print(quiz)

        # print(form)
        # print(files)

        # quiz_type = form['quiz_type']
        # if quiz_type == 'person':
        #     handle_person_quiz(form, files, quiz)
        # elif quiz_type == 'percent':
        #     handle_percent_quiz(form, quiz)

        # image = resize(files['quiz_preview'].stream)
        # if files['quiz_preview']:
        #     alice = upload_image(resize(files['quiz_preview'].stream, (1000, 700)))
        #     quiz['image'] = alice['image']['id']

        return redirect('/')
    return render_template('createquiz.html')


# @login_manager.unauthorized_handler
# def unauthorized():
#     return 'Сначала войдите в аккаунт'


def collect_personQuiz_data(form: ImmutableMultiDict, files: ImmutableMultiDict[str, FileStorage], quiz: dict):
    characters = collect_data(form, 'person{i}', '{i}')
    quiz['characters'] = []
    for name, character in characters.items():
        imageBytes = BytesIO()
        image = resize(files[f'{name}_image'].stream)
        image.show()
        image.save(imageBytes, format=image.format)

        quiz['characters'].append(
            {
                "name": character,
                "description": form[f'{name}_description'],
                "image": imageBytes
            }
        )

    questions = collect_data(form, 'question{i}', '{i}')
    quiz['questions'] = []
    for question_name, question in questions.items():
        quiz['questions'].append(
            {
                "title": question,
                "answers": []
            }
        )
        answers = quiz['questions'][-1]['answers']
        for answer_name, title in collect_data(form, question_name+'_answer{i}', '{i}'):
            answers.append(
                {
                    "title": title
                }
            )


def collect_percentQuiz_data(form: ImmutableMultiDict, files: ImmutableMultiDict[str, FileStorage], quiz: dict):
    pass


def collect_data(data: ImmutableMultiDict, template: str, iterator: str):
    i = 1
    collectedData = {}
    while True:
        name = template.replace(iterator, str(i))
        if name not in data:
            return collectedData
        collectedData[name] = data[name]
        i += 1


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
                        # проверить получаются ли так нужные данные списком
                        'characters': field.characters.data
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


def upload_image(image_bits):
    alice_url = 'https://dialogs.yandex.net/api/v1/skills/84636ff1-4b07-4385-ab89-21a817d2a74d/images'
    headers = {
        'Authorization': 'OAuth y0_AgAAAAA955vEAAT7owAAAADfy__rBzw4lsvtRomHf17r4hPBvgCP3Os'}
    files = {'file': image_bits}
    response = requests.post(url=alice_url, headers=headers, files=files)
    return response.json()


def delete_image(image_id):
    alice_url = f'https://dialogs.yandex.net/api/v1/skills/84636ff1-4b07-4385-ab89-21a817d2a74d/images/{image_id}'
    headers = {
        'Authorization': 'OAuth y0_AgAAAAA955vEAAT7owAAAADfy__rBzw4lsvtRomHf17r4hPBvgCP3Os'}
    response = requests.delete(url=alice_url, headers=headers)
    return response.json()


def main():
    db_session.global_init('db/ya_quiz.db')
    api.add_resource(quizzes_resources.QuizResource, "/api/quiz/<int:quiz_id>")
    api.add_resource(quizzes_resources.QuizListResource, "/api/quiz")
    app.run(port=8080, host='127.0.0.1')


if __name__ == "__main__":
    main()
