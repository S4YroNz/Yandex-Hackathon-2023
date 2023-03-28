import random

from flask import Flask, request, jsonify
from typing import Dict
from wordVariations import VARIATIONS
import logging
import requests
import json


app = Flask(__name__)


logging.basicConfig(level=logging.INFO)


class User:
    def __init__(self, id_):
        self.id = id_
        self.isNew = True
        self.inQuiz = False
        self.justFinished = True
        self.requests = 0


sessionStorage: Dict[str, User] = {}


class _nlu:
    def __init__(self, r: dict):
        self.tokens: list[str] = r['tokens']
        self.entities: list[dict] = r['entities']


class _sessionUser:
    def __init__(self, r: dict):
        self.user_id: str = r['user_id']
        self.access_token: str = r.get('access_token', None)

    def todict(self):
        return vars(self)


class _reqSession:
    def __init__(self, r: dict):
        self.message_id: int = r['message_id']
        self.session_id: str = r['session_id']
        self.skill_id: str = r['skill_id']
        self.user_id: str = r['user_id']
        self.user = _sessionUser(r['user'])
        self.application = r['application']
        self.new: bool = r['new']

    def todict(self):
        a = {}
        for key, value in vars(self).items():
            if not isinstance(value, (str, int, bool, list, dict)):
                a[key] = value.todict()
            else:
                a[key] = value
        return a


class _request:
    def __init__(self, r: dict):
        self.type: str = r['type']
        self.nlu = _nlu(r['nlu'])
        self.command: str = r.get('command', None)
        self.original_utterance: str = r.get('original_utterance', None)
        self.markup: dict = r.get('markup', None)
        self.payload: dict = r.get('payload', None)

    def todict(self):
        a = {}
        for key, value in vars(self).items():
            if not isinstance(value, (str, int, bool, list, dict)):
                a[key] = value.todict()
            else:
                a[key] = value
        return a


class Req:
    def __init__(self, r: dict):
        self.meta = r['meta']
        self.request = _request(r['request'])
        self.session = _reqSession(r['session'])
        self.state: dict = r.get('state', None)
        self.version: str = r['version']


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    req = Req(request.json)
    response = {
        'session': req.session.todict(),
        'version': req.version,
        'response': {
            'end_session': False
        }
    }
    handle_dialog(req, response)

    logging.info(f'Response:  {response!r}')

    return jsonify(response)


def check_tokens(tokens, variation):
    for token in tokens:
        if token in VARIATIONS[variation]:
            return True
    return False


def handle_dialog(req: Req, res):
    user_id = req.session.user_id
    if req.session.new:
        sessionStorage[user_id] = User(user_id)
        send_greetings(res)
        return
    sessionStorage[user_id].requests += 1

    tokens = req.request.nlu.tokens
    print(sessionStorage[user_id].isNew, sessionStorage[user_id].inQuiz)

    if sessionStorage[user_id].isNew:
        if check_tokens(tokens, 'да'):
            res['response']['text'] = 'Начинаю случайную викторину'
            sessionStorage[user_id].inQuiz = True
            send_quizSuggests(res)
            return
        elif check_tokens(tokens, 'нет'):
            res['response']['text'] = 'Хорошо, тогда можешь посмотреть топ викторин'
            send_idleSuggests(res)
            return

    if sessionStorage[user_id].inQuiz:
        if check_tokens(tokens, 'выход'):
            res['response']['text'] = 'Хорошо, выхожу из викторины'
            sessionStorage[user_id].inQuiz = False
            send_idleSuggests(res)
            return
        if check_tokens(tokens, 'повтори'):
            res['response']['text'] = 'Повторяю вопрос'
            send_quizSuggests(res)
            return

    if not sessionStorage[user_id].inQuiz:
        if sessionStorage[user_id].justFinished:
            if check_tokens(tokens, 'заново'):
                res['response']['text'] = 'Запускаю эту же викторину заново'
                sessionStorage[user_id].justFinished = False
                sessionStorage[user_id].inQuiz = True
                send_idleSuggests(res)
                return
        if check_tokens(tokens, 'топ викторин'):
            res['response']['text'] = 'Вывела топ викторин'
            send_idleSuggests(res)
            return
        if check_tokens(tokens, 'случайная викторина'):
            res['response']['text'] = 'Начинаю случайную викторину'
            sessionStorage[user_id].inQuiz = True
            send_quizSuggests(res)
            return
        if check_tokens(tokens, 'создание викторины'):
            res['response']['text'] = 'Чтобы создать викторину, перейдите по ссылке. Удачи сделать классную викторину!'
            send_idleSuggests(res)
            send_creationSuggest(res)
            return
        if check_tokens(tokens, 'умения'):
            res['response']['text'] = "Я могу запустить случайную или выбранную тобой викторину, \
могу вывести топ самых проходимых. А если ты не нашел той викторины, которую хотел пройти, \
можешь сам ее создать"
            send_idleSuggests(res)
            return
        if check_tokens(tokens, 'правила'):
            res['response']['text'] = "Викторины состоят из нескольких вопросов, в ответ на каждый ты\
можешь выбрать один вариант из нескольких предложенных. Ответив на каждый вопрос, ты узнаешь результат"
            send_idleSuggests(res)
            return

    sessionStorage[user_id].justFinished = False
    sessionStorage[user_id].isNew = False
    send_error(res)
    if sessionStorage[user_id].inQuiz:
        send_quizSuggests(res)
    else:
        send_idleSuggests(res)


def send_idleSuggests(res):
    res['response']['buttons'] = [
        {
            "title": "Топ✨",
            "hide": True
        },
        # {
        #     "title": "Викторина ...",
        #     "hide": True
        # },
        {
            "title": "Случайная🎲",
            "hide": True
        },
        {
            "title": "Создать🤖",
            "hide": True
        },
        {
            "title": "Что ты умеешь?🤔",
            "hide": True
        },
        {
            "title": "Помощь😣",
            "hide": True
        }
    ]


def send_quizSuggests(res):
    res['response']['buttons'] = [
        {
            "title": "Выход",
            "hide": True
        },
        {
            "title": "Повтори вопрос",
            "hide": True
        }
    ]


def send_creationSuggest(res):
    res['response']['buttons'] = res['response'].get('buttons', []) + [
        {
            "title": "Создать",
            "url": "https://youtube.com",
            "hide": False
        }
    ]


def send_error(res):
    res['response']['text'] = "Извини, я не поняла, повтори пожалуйста"


def random_quiz(user_id):
    sessionStorage[user_id]['status'] = 'passing_the_quiz'
    sessionStorage[user_id]['current_quiz'] = random.randint(0, len(sessionStorage['quizzes']))
    sessionStorage[user_id]['current_question'] = 0
    return


def download_image_by_bits(image_bits):
    alice_url = 'https://dialogs.yandex.net/api/v1/skills/a9331dba-12d5-41be-ba3b-d691a6294153/images'
    headers = {'Authorization': 'OAuth y0_AgAAAAAhKRZBAAT7owAAAADfkTMUOctm8BgkQU-3pQ8X_Vd5UK3G1qw'}
    files = {'file': image_bits}
    req = requests.post(url=alice_url, headers=headers, files=files)
    return req.json()


def delete_image(image_id):
    alice_url = f'https://dialogs.yandex.net/api/v1/skills/a9331dba-12d5-41be-ba3b-d691a6294153/images/{image_id}'
    headers = {'Authorization': 'OAuth y0_AgAAAAAhKRZBAAT7owAAAADfkTMUOctm8BgkQU-3pQ8X_Vd5UK3G1qw'}
    req = requests.delete(url=alice_url, headers=headers)
    return req.json()


def greeting():
    result = {
        'text': '''
    Привет! Я управляющая викторинами ЯQuiz. У меня есть викторины для всех и каждого. Начнем случайную викторину?
    ''',
        'buttons': [
            {
            "title": "Да, давай",
            "payload": {},
            "hide": True
        },
        {
            "title": "Нет",
            "payload": {},
            "hide": True
        }
    ]


if __name__ == '__main__':
    app.run()
