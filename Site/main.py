from flask import Flask, render_template
import logging

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def sign_up():
    return render_template('signup.html')

@app.route('/signup/post', methods=['POST'])
def sign_up_handle():
    #TODO: регестрация
    pass

@app.route('/signin')
def sign_in():
    return render_template('signin.html')

@app.route('/signin/post', methods=['POST'])
def sign_in_handle():
    #TODO: вход в аккаунт
    pass

#TODO: база данных аккаунтов вида
# [id(key, int), username(str, включить индексацию), hashed_password(str), ownedQuizes(str тут будут id quiz'ов через пробел)]

if __name__ == "__main__":
    app.run(port=8080, host='127.0.0.1')