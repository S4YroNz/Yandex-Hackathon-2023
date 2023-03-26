
from flask import Flask, request, jsonify
import logging


app = Flask(__name__)


logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    user_answer = req['request']['original_utterance'].lower()
    if req['session']['new']:
        sessionStorage['user_id']['status'] = 'start'
        greet = greeting()
        res['response']['text'] = greet['text']
        res['response']['buttons'] = greet['buttons']
        return
    if sessionStorage['user_id']['status'] == 'start':

        if user_answer == "да, давай":
            random_quiz()
            passing_the_quiz()
        elif user_answer == 'нет':
            res['response']['text'] = 'Хорошо, тогда можешь посмотреть топ викторин'
            res['response']['card'] = show_top()['card']
        else:
            res['response']['text'] = unrecognized_phrase()['text']
        return
    if sessionStorage['user_id']['status'] == 'passing_the_quiz':
        if user_answer in ['выход', 'стоп']:
            res['response']['text'] = 'Хорошо, выхожу из викторины'
            sessionStorage['user_id']['status'] = 'idling'
        else:
            passing_the_quiz()
        return
    if sessionStorage['user_id']['status'] == 'idling':
        if user_answer == 'выведи топ викторин':
            show_top()
        elif 'запусти викторину' in user_answer:
            sessionStorage['user_id']['current_quiz'] = user_answer.split('запусти викторину')[-1].strip()
            sessionStorage['user_id']['status'] = 'passing_the_quiz'
            sessionStorage['user_id']['current_question'] = 0
            passing_the_quiz()
        elif user_answer == 'запусти случайную викторину':
            random_quiz()
        elif user_answer == 'я хочу создать викторину':
            create_quiz()
        elif user_answer == 'что ты можешь?':
            res['response']['text'] = '''Я могу запустить случайную или выбранную тобой викторину, 
            могу вывести топ самых проходимых. А если ты не нашел той викторины, которую хотел пройти,  
            можешь сам ее создать'''
            res['response']['buttons'] = get_idle_suggests()
        elif user_answer == 'расскажи правила':
            res['response']['text'] = '''Викторины состоят из нескольких вопросов, в ответ на каждый ты
             можешь выбрать один вариант из нескольких предложенных. Ответив на каждый вопрос, ты узнаешь результат'''
            res['response']['buttons'] = get_idle_suggests()

def get_idle_suggests():
    result = {
         'buttons': []
     }
    return result
def create_quiz():
    return
def unrecognized_phrase():
    result = {
        'text': 'Извини, я тебя не поняла, повтори пожалуйста'
    }
    return result


def show_top():
    result = {
        'card': {
            'type' : 'ItemList',
            "header": {
                "text": "Заголовок списка изображений",
            },
            'items': []
        },
        'buttons': [
            {
                "title": "Викторина 1",
                "payload": {},
                "hide": True
            },
            {
                "title": "Викторина 2",
                "payload": {},
                "hide": True
            }
        ]


    }
    return result
def passing_the_quiz():
    # TODO: Прохождение квиза
    return
def random_quiz():
    sessionStorage['user_id']['status'] = 'passing_the_quiz'
    # TODO: Выбор рандомного квиза
    sessionStorage['user_id']['current_quiz'] = 'quiz_name'
    sessionStorage['user_id']['current_question'] = 0
    return


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

    }
    return result

if __name__ == '__main__':
    app.run()