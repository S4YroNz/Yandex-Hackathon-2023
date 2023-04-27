import os
import json
from flask import Flask, render_template, redirect, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
import requests
import logging
import base64
from werkzeug.datastructures import ImmutableMultiDict, FileStorage

from myapp.forms.user import *
from myapp.data import db_session, quizzes_resources
from myapp.data.users import User
from myapp.data.quizzes import Quiz
from myapp.imageResize import resize

# Flask app initializing
app = Flask(__name__)
app.secret_key = os.urandom(12)
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
@login_required
def index():
    db_sess = db_session.create_session()
    quizzes = db_sess.query(Quiz).filter(Quiz.owner_id == current_user.id).all()
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

@login_manager.unauthorized_handler
def unauthorized():
    return render_template('unauthorized.html')


def get_image(files, name):
    if not files[name].filename:
        return

    file: FileStorage = files[name]
    file.save('temp.png')
    with open('temp.png', 'rb') as f:
        data = f.read()
    os.remove('temp.png')

    return base64.encodebytes(data).decode('utf-8')


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
            collect_person_quiz_data(form, files, quiz)
        else:
            collect_percent_quiz_data(form, quiz)

        string = json.dumps(quiz, ensure_ascii=False)
        db_sess = db_session.create_session()
        db_sess.add(
            Quiz(
                owner_id=current_user.id,
                json=string,
                title=quiz['title'],
                views=0
            )
        )
        db_sess.commit()

        return render_template('quizsended.html')
    return render_template('createquiz.html')


def collect_person_quiz_data(form, files, quiz):
    characters = collect_data(form, 'person{i}', '{i}')
    quiz['characters'] = []
    for name, character in characters.items():
        imgBytes = get_image(files, f'{name}_image')

        quiz['characters'].append(
            {
                "name": character,
                "description": form[f'{name}_description'],
                "image": imgBytes
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
        for answer_name, title in collect_data(form, question_name+'_answer{j}', '{j}').items():
            print(f'ANSWER {answer_name}', form[f'{answer_name}_select'])
            answers.append(
                {
                    "title": title,
                    "character": quiz['characters'][int(form[f'{answer_name}_select'][len('person'):]) - 1]['name']
                }
            )


def collect_percent_quiz_data(form, quiz):
    questions = collect_data(form, 'question{i}', '{i}')
    quiz['questions'] = []
    for question_name, question in questions.items():
        answers = []
        print(*enumerate(collect_data(form, question_name+'_answer{j}', '{j}').items(), start=1))
        print(form[f'{question_name}_radio'])
        for i, title in enumerate(collect_data(form, question_name+'_answer{j}', '{j}').values(), start=1):
            answers.append(
                {
                    "title": title,
                    "is_true": int(form[f'{question_name}_radio']) == i
                }
            )
        quiz['questions'].append(
            {
                "title": question,
                "answers": answers
            }
        )
    pass


def collect_data(data, template, iterator):
    i = 1
    collectedData = {}
    while True:
        name = template.replace(iterator, str(i))
        if name not in data:
            return collectedData
        collectedData[name] = data[name]
        i += 1


# @app.route('/quiz/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit_quiz(id):
#     if request.method == "GET":
#         db_sess = db_session.create_session()
#         quiz = db_sess.query(Quiz).filter(Quiz.id == id, Quiz.owner_id == current_user.id).first()
#         if quiz:
#             with open('output.json') as file: # Получение данных из бд
#                 data = json.load(file)
#             return render_template('quiz.html', data=data)
#         else:
#             return render_template('noquiz.html')
#     return abort(404)


@app.route('/deletequiz/<int:id>')
@login_required
def delete_quiz(id):
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == id, Quiz.owner_id == current_user.id).first()
    if quiz:
        os.remove('output.json')
        # db_sess.delete(quiz)
        # db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def create_app():
    db_session.global_init()
    db_session.create_session()
    api.add_resource(quizzes_resources.QuizResource, "/api/quiz/<int:quiz_id>")
    api.add_resource(quizzes_resources.QuizListResource, "/api/quiz")
    api.add_resource(quizzes_resources.QuizListTitles, "/api/quiz_titles")
    return app

def upload_image(img_bytes):
    alice_url = 'https://dialogs.yandex.net/api/v1/skills/84636ff1-4b07-4385-ab89-21a817d2a74d/images'
    headers = {
        'Authorization': 'OAuth y0_AgAAAAA955vEAAT7owAAAADfy__rBzw4lsvtRomHf17r4hPBvgCP3Os'
    }
    files = {'file': img_bytes}
    response = requests.post(url=alice_url, headers=headers, files=files)
    return response.json()


def delete_image(image_id):
    alice_url = f'https://dialogs.yandex.net/api/v1/skills/84636ff1-4b07-4385-ab89-21a817d2a74d/images/{image_id}'
    headers = {
        'Authorization': 'OAuth y0_AgAAAAA955vEAAT7owAAAADfy__rBzw4lsvtRomHf17r4hPBvgCP3Os'}
    response = requests.delete(url=alice_url, headers=headers)
    return response.json()