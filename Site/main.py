from flask import Flask, render_template, redirect
from forms.user import *
from data import db_session
from data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user

# Flask app initializing
app = Flask(__name__)
app.config['SECRET_KEY'] = '908jyuh0j67f453v5439hj78y0yvcrt9ew80ny'

# LoginManager initializing
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init('db/ya_quiz.db')
    app.run(port=8080, host='127.0.0.1')


@app.route('/')
def index():
    return render_template('index.html')


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


@app.route('/createquiz')
def create_quiz():
    return render_template('createquiz.html')


# TODO: база данных аккаунтов вида
# [id(key, int), username(str, включить индексацию), hashed_password(str), ownedQuizes(str тут будут id quiz'ов через пробел)]

if __name__ == "__main__":
    main()
