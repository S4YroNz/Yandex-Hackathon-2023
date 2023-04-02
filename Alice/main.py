import random
import requests
import json


class User:
    def __init__(self, r: dict):
        self.is_new = r.get('is_new', True)
        self.in_quiz = r.get('in_quiz', False)
        self.preview_quiz = r.get('preview_quiz', False)
        self.just_finished = r.get('just_finished', False)
        self.quiz_id = r.get('quiz_id', None)
        self.lastquiz_id = r.get('lastquiz_id', None)
        self.cur_question = r.get('cur_question', None)
        self.result = r.get('result', {})

    def toDict(self):
        return {key: value for key, value in vars(self).items()}


with open('phraseVariable.json', encoding='utf-8') as file:
    phraseVariables = json.load(file)
with open('all_quizzes.json', encoding='utf-8') as file:
    quizzes = json.load(file)['quizzes']


def main(event, context):
    user = User(event.get('state', {}).get('session', {}))
    res = {
        'session': event['session'],
        'version': event['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(event, res, user)
    res['session_state'] = user.toDict()

    cutTooLongText(res)
    return res


def cutTooLongText(res):
    a = res['response']['text']
    if len(a) > 1024:
        res['response']['text'] = a[:1022] + '..'
        return


def handle_dialog(req: dict, res, user: User):
    if req['session']['new']:
        send_greetings(res)
        send_yesno_suggest(res)
        return

    intents = req['request']['nlu']['intents']
    if user.is_new:
        user.is_new = False
        if 'YANDEX.CONFIRM' in intents:
            preview_quiz(user, res, random.randint(0, len(quizzes) - 1))
            return
        elif 'YANDEX.REJECT' in intents:
            res['response']['text'] = 'Хорошо, тогда можешь посмотреть топ викторин'
            send_idle_suggests(res)
            return

    if user.preview_quiz:
        # user.preview_quiz = False
        if 'YANDEX.CONFIRM' in intents:
            start_quiz(user)
            handle_quiz(req, res, user, False)
            send_quiz_suggests(res, user)
            return
        elif 'YANDEX.REJECT' in intents:
            exit_quiz(user)
            res['response']['text'] = random.choice(
                phraseVariables['exit_from_quiz'])
            send_idle_suggests(res)
            return

    if user.in_quiz:
        quiz = quizzes[user.quiz_id]
        if user.cur_question < len(quiz['questions']) - 1:
            if 'STOP' in intents:
                exit_quiz(user)
                res['response']['text'] = random.choice(
                    phraseVariables['exit_from_quiz'])
                send_idle_suggests(res)
                return
            if handle_quiz(req, res, user, 'REPEAT_QUESTION' not in intents):
                send_quiz_suggests(res, user)
                return
        elif user.cur_question == len(quiz['questions']) - 1:
            send_quiz_result(req, res, user)
            return

    if 'YANDEX.HELP' in intents:
        res['response']['text'] = "Викторины состоят из нескольких вопросов, в ответ на каждый ты\
можешь выбрать один вариант из нескольких предложенных. Ответив на каждый вопрос, ты узнаешь результат"
        user.preview_quiz = False
        if user.in_quiz:
            send_quiz_suggests(res, user)
        else:
            send_idle_suggests(res)
        return

    if not user.in_quiz:
        if user.just_finished:
            if 'YANDEX.REPEAT' in intents:
                res['response']['text'] = random.choice(
                    phraseVariables['repeat_quiz'])
                user.just_finished = False
                user.in_quiz = True
                send_idle_suggests(res)
                return
        if 'START_QUIZ' in intents:
            user.preview_quiz = False
            quiz = intents['START_QUIZ']['slots']['quiz_title']['value']
            res['response']['text'] = f'Вы захотели запустить викторину {quiz}'
            send_idle_suggests(res)
            return
        if 'SHOW_TOP' in intents:
            user.preview_quiz = False
            res['response']['text'] = 'Вывела топ'
            send_idle_suggests(res)
            return
        if 'START_RANDOM_QUIZ' in intents:
            user.preview_quiz = False
            preview_quiz(user, res, random.randint(0, len(quizzes) - 1))
            return
        if 'CREATE_QUIZ' in intents:
            user.preview_quiz = False
            res['response']['text'] = random.choice(
                phraseVariables['create_quiz'])
            send_idle_suggests(res)
            send_creation_suggest(res)
            return
        if 'WHAT_YOU_CAN_DO' in intents:
            user.preview_quiz = False
            res['response']['text'] = "Я могу запустить случайную или выбранную тобой викторину, \
    могу вывести топ самых проходимых. А если ты не нашел той викторины, которую хотел пройти, \
    можешь сам ее создать."
            send_idle_suggests(res)
            return

    if user.just_finished and 'REPEAT_QUIZ' in intents:
        preview_quiz(user, res, user.lastquiz_id)
        return

    if 'STOP' in intents:
        res['response']['text'] = 'До встречи в следующий раз!'
        res['response']['end_session'] = True
        return

    user.just_finished = False
    user.is_new = False
    if user.in_quiz:
        send_in_quiz_error(res)
    else:
        send_error(res)
    if user.in_quiz:
        if user.cur_question == -1:
            send_yesno_suggest(res)
        else:
            send_quiz_suggests(res, user)
    else:
        send_idle_suggests(res)


def handle_quiz(req, res, user: User, next_=True):
    # Получение ответа
    if user.cur_question != -1 and next_:
        if not check_quizAnswer(req, res, user):
            return False

    # Следующий вопрос
    user.cur_question += 1 if next_ else 0
    question = quizzes[user.quiz_id]['questions'][user.cur_question]
    title = question['title']
    answers = [i['title'] for i in question['answers']]
    res['response']['text'] = title + "\n" + \
        "\n".join(f"{i}. {row}" for i, row in enumerate(answers, start=1))
    return True


def check_quizAnswer(req, res, user: User):
    intents = req['request']['nlu']['intents']
    quiz = quizzes[user.quiz_id]
    question = quiz['questions'][user.cur_question]
    answers = question['answers']
    if not ('CHOOSE_ANSWER_2' in intents or 'CHOOSE_ANSWER_1' in intents):
        send_error(res)
        return False
    user_answer = intents['CHOOSE_ANSWER_1'] if 'CHOOSE_ANSWER_1' in intents else intents['CHOOSE_ANSWER_2']
    user_answer = user_answer['slots']['answer_number']['value']
    if not (0 < user_answer <= len(answers)):
        res['response']['text'] = f'Ответов всего {len(answers)}, назови другой'
        return False

    # Начисление очков
    if quiz['type'] == 'person':
        for character in answers[user_answer - 1]['characters']:
            user.result[character] += 1
    elif quiz['type'] == 'percent':
        correct = [i for i, a in enumerate(
            question['answers'], start=1) if a['is_true']][0]
        if user_answer == correct:
            user.result += 1
    return True


def send_quiz_result(req, res, user: User):
    # Проверка последнего ответа
    check_quizAnswer(req, res, user)

    # Вывод результата
    quiz = quizzes[user.quiz_id]
    if quiz['type'] == 'person':
        result = max(user.result.items(), key=lambda x: x[1])[0]
        text = f'Ты - {result}'
        res['response']['text'] = text
        character = [i for i in quiz['characters'] if i['name'] == result][0]
        if character['image']:
            res['response']['card'] = {}
            card = res['response']['card']
            card['type'] = 'BigImage'
            card['title'] = text
            card['description'] = character['description']
            card['image_id'] = character['image']
    elif quiz['type'] == 'percent':
        result = round(
            user.result / len(quizzes[user.quiz_id]['questions']) * 100)
        res['response']['text'] = f'Ваш результат - {result}%. Вы можете пройти заново эту викторину или начать другую'

    send_idle_suggests(res)
    res['response']['buttons'] = [
        {
            "title": "Заново 🔁",
            "hide": True
        }
    ] + res['response']['buttons']

    # Выход из Виткторины
    user.lastquiz_id = user.quiz_id
    user.in_quiz = False
    user.quiz_id = None
    user.cur_question = None
    user.just_finished = True
    user.result = {}
    return


def preview_quiz(user: User, res, quiz_id):
    user.quiz_id = quiz_id
    user.preview_quiz = True

    # Превью
    title = quizzes[user.quiz_id]['title']
    description = quizzes[user.quiz_id]['description']
    creator = quizzes[user.quiz_id]['creator']
    preview = quizzes[user.quiz_id]['image']
    res['response']['text'] = f"{title}\n{description}\nСоздатель:{creator}\nНачинаем?"
    if quizzes[user.quiz_id]['image']:
        res['response']['card'] = {}
        card = res['response']['card']
        card['type'] = 'BigImage'
        card['image_id'] = preview
        card['title'] = f'{title}'
        card['description'] = f'{description}\nСоздатель: {creator}\nНачинаем?'
    send_yesno_suggest(res)


def start_quiz(user: User):
    user.in_quiz = True
    user.cur_question = 0
    quiz = quizzes[user.quiz_id]
    if quiz['type'] == 'person':

        user.result = {character['name']
            : 0 for character in quiz['characters']}
    elif quiz['type'] == 'percent':
        user.result = 0


def exit_quiz(user: User):
    user.quiz_id = None
    user.cur_question = None
    user.in_quiz = False
    user.just_finished = False
    user.result = {}


def send_idle_suggests(res):
    hide = True
    res['response']['buttons'] = [
        {
            "title": "Топ ✨",
            "hide": hide
        },
        {
            "title": "Случайная викторина 🎲",
            "hide": hide
        },
        {
            "title": "Создать викторину 🤖",
            "hide": hide
        },
        {
            "title": "Что ты умеешь? 🤔",
            "hide": hide
        },
        {
            "title": "Помощь",
            "hide": hide
        }
    ]


def send_quiz_suggests(res, user: User):
    answers = len(quizzes[user.quiz_id]['questions']
                  [user.cur_question]['answers'])
    res['response']['buttons'] = [
        *[
            {
                "title": f"{i}",
                "hide": True
            }
            for i in range(1, answers + 1)
        ],
        {
            "title": "Повтори",
            "hide": True
        },
        {
            "title": "Выход",
            "hide": True
        },
    ]


def send_creation_suggest(res):
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


def send_yesno_suggest(res):
    res['response']['buttons'] = [
        {
            "title": random.choice(phraseVariables['yes']),
            "hide": True
        },
        {
            "title": "Нет",
            "hide": True
        }
    ]


def send_in_quiz_error(res):
    res['response']['text'] = random.choice(phraseVariables['quiz_error'])


def send_error(res):
    res['response']['text'] = "Извини, я не поняла, повтори пожалуйста"


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
