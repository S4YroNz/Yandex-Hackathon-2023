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
        self.justFinished = False
        self.quizId = None
        self.questionId = None


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
        self.result = {}


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
    user_answer = req['request']['nlu']['intents']
    if req.session.new:
        sessionStorage['quizzes'] = requests.get('http://адрес нашего сайта/api/quiz').json()['quiz']
        sessionStorage[user_id] = User(user_id)
        send_greetings(res)
        return
    sessionStorage[user_id].requests += 1

    tokens = req.request.nlu.tokens
    print(sessionStorage[user_id].isNew, sessionStorage[user_id].inQuiz)

    if sessionStorage[user_id].isNew:
        if 'YANDEX.CONFIRM' in user_answer:
            res['response']['text'] = 'Начинаю случайную викторину'
            sessionStorage[user_id].inQuiz = True
            send_quizSuggests(res)
            return
        elif 'YANDEX.REJECT' in user_answer:
            res['response']['text'] = 'Хорошо, тогда можешь посмотреть топ викторин'
            send_idleSuggests(res)
            return

    if sessionStorage[user_id].inQuiz:
        if 'STOP' in user_answer:
            res['response']['text'] = 'Хорошо, выхожу из викторины'
            sessionStorage[user_id].inQuiz = False
            send_idleSuggests(res)
            return
        if 'YANDEX.REPEAT' in user_answer:
            res['response']['text'] = 'Повторяю вопрос'
            send_quizSuggests(res)
            return

    if not sessionStorage[user_id].inQuiz:
        if sessionStorage[user_id].justFinished:
            if 'YANDEX.REPEAT' in user_answer:
                res['response']['text'] = 'Запускаю эту же викторину заново'
                sessionStorage[user_id].justFinished = False
                sessionStorage[user_id].inQuiz = True
                send_idleSuggests(res)
                return
        if 'SHOW_TOP' in user_answer:
            res['response']['text'] = 'Вывела топ викторин'
            send_idleSuggests(res)
            return
        if 'START_RANDOM_QUIZ' in user_answer:
            res['response']['text'] = 'Начинаю случайную викторину'
            sessionStorage[user_id].inQuiz = True
            send_quizSuggests(res)
            return
        if 'CREATE_QUIZ' in user_answer:
            res['response']['text'] = 'Чтобы создать викторину, перейдите по ссылке. Удачи сделать классную викторину!'
            send_idleSuggests(res)
            send_creationSuggest(res)
            return
        if 'WHAT_YOU_CAN_DO' in user_answer:
            res['response']['text'] = "Я могу запустить случайную или выбранную тобой викторину, \
могу вывести топ самых проходимых. А если ты не нашел той викторины, которую хотел пройти, \
можешь сам ее создать"
            send_idleSuggests(res)
            return
        if 'YANDEX.HELP' in user_answer:
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


def send_greetings(res):
    res['response']['text'] = "Привет! Я управляющая викторинами ЯQuiz. У меня есть викторины для всех и каждого. Начнем случайную викторину?"
    res['response']['tts'] = "Привет! Я управляющая викторинами ЯQuiz. У меня есть викторины для всех и каждого. Начнем случайную викторину?"
    res['response']['buttons'] = [
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


def send_error(res):
    res['response']['text'] = "Извини, я не поняла, повтори пожалуйста"


def passing_the_quiz(req, res):
    # TODO: загрузку фото и кнопки вариантов ответов
    # Для прохождения нужно id квиза и № вопроса
    # Храним их в sessionStorage
    user_id = req['session']['user_id']
    session = sessionStorage[user_id]
    quiz_id = ['current_quiz']
    quest_numb = session['current_question']
    quiz = sessionStorage['quizzes'][quiz_id]
    if quest_numb == 0:
        res['response']['text'] = f"""{quiz['title']}\n\n{quiz['description']}\n от {quiz['creator']}"""
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = 'Где выводится это сообщение?'
        res['response']['card']['image_id'] = 'id картинки'
        if quiz['type'] == 'percent':
            session['result'] = 0
        else:
            session['result'] = {}
            for pers in quiz['characters']:
                session['result'][pers['title']] = 0
    elif quest_numb <= len(quiz['questions']):
        question = quiz['questions'][quest_numb - 1]
        answers = '\n'.join(
            [f"{i + 1}. {value['title']}" for i, value in question['answers']])
        res['response']['text'] = f"""{question['title']}\n\n{answers}"""
    else:
        if quiz['type'] == 'person':
            result = max(session['result'].values())
            for key, value in session['result'].items():
                if value == result:
                    result = key
                    break
            result = list(
                filter(lambda x: x['title'] == result, quiz['characters']))[0]
            res['response']['text'] = f"""Поздравляем! Вы - {result['title']}!\n{result['description']}"""
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Ваш персонаж'
            res['response']['card']['image_id'] = 'id картинки'
        else:
            res['response'][
                'text'] = f"""Поздравляем! Вы ответили правильно на {int(100 * session['result'] / len(quiz['questions']))}%"""

    if 1 <= quest_numb <= len(quiz['questions']):
        answer = int(req['request']['original_utterance'])  # id + 1 ответа
        if quiz['type'] == 'percent':
            if quiz['questions'][quest_numb - 2]['answers'][answer - 1]['is_true']:
                session['result'] += 1
        else:
            for pers in quiz['questions'][quest_numb - 2]['answers'][answer - 1]['characters']:
                session['result'][pers] += 1

    session['current_question'] += 1
    sessionStorage[user_id] = session
    return


def random_quiz(user_id):
    sessionStorage[user_id]['status'] = 'passing_the_quiz'
    sessionStorage[user_id]['current_quiz'] = random.randint(
        0, len(sessionStorage['quizzes']))
    sessionStorage[user_id]['current_question'] = 0
    return


def download_image_by_bits(image_bits):
    alice_url = 'https://dialogs.yandex.net/api/v1/skills/a9331dba-12d5-41be-ba3b-d691a6294153/images'
    headers = {
        'Authorization': 'OAuth y0_AgAAAAAhKRZBAAT7owAAAADfkTMUOctm8BgkQU-3pQ8X_Vd5UK3G1qw'}
    files = {'file': image_bits}
    req = requests.post(url=alice_url, headers=headers, files=files)
    return req.json()


def delete_image(image_id):
    alice_url = f'https://dialogs.yandex.net/api/v1/skills/a9331dba-12d5-41be-ba3b-d691a6294153/images/{image_id}'
    headers = {
        'Authorization': 'OAuth y0_AgAAAAAhKRZBAAT7owAAAADfkTMUOctm8BgkQU-3pQ8X_Vd5UK3G1qw'}
    req = requests.delete(url=alice_url, headers=headers)
    return req.json()


if __name__ == '__main__':
    app.run()
