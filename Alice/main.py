import random
import requests as requests_lib
import json


class User:
    def __init__(self, r: dict):
        self.isNew = r.get('isNew', True)
        self.inQuiz = r.get('inQuiz', False)
        self.previewQuiz = r.get('previewQuiz', False)
        self.justFinished = r.get('justFinished', False)
        self.quizId = r.get('quizId', None)
        self.lastQuizId = r.get('lastQuizId', None)
        self.curQuestion = r.get('curQuestion', None)
        self.result = r.get('result', {})

    def toDict(self):
        return {key: value for key, value in vars(self).items()}


with open('phraseVariable.json', encoding='utf-8') as file:
    phraseVariables = json.load(file)
with open('all_quizzes.json', encoding='utf-8') as file:
    quizzes = json.load(file)['quizzes']


class _nlu:
    def __init__(self, r: dict):
        self.tokens: list[str] = r['tokens']
        self.entities: list[dict] = r['entities']
        self.intents: list[dict] = r['intents']


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


def main(event, context):
    print(f'EVENT: {event!r}')
    print(f'CONTEXT: {context!r}')

    req = Req(event)
    user = User(event.get('state', {}).get('session', {}))
    res = {
        'session': req.session.todict(),
        'version': req.version,
        'response': {
            'end_session': False
        }
    }
    handle_dialog(req, res, user)
    res['session_state'] = user.toDict()

    return res


def handle_dialog(req: Req, res, user: User):
    if req.session.new:
        send_greetings(res)
        send_yesnoSuggest(res)
        return

    intents = req.request.nlu.intents
    if user.isNew:
        user.isNew = False
        if 'YANDEX.CONFIRM' in intents:
            preview_quiz(user, res, random.randint(0, len(quizzes) - 1))
            return
        elif 'YANDEX.REJECT' in intents:
            res['response']['text'] = 'Хорошо, тогда можешь посмотреть топ викторин'
            send_idleSuggests(res)
            return

    if user.previewQuiz:
        # user.previewQuiz = False
        if 'YANDEX.CONFIRM' in intents:
            start_quiz(user)
            handle_quiz(req, res, user, False)
            send_quizSuggests(res, user)
            return
        elif 'YANDEX.REJECT' in intents:
            exit_quiz(user)
            res['response']['text'] = random.choice(
                phraseVariables['exit_from_quiz'])
            send_idleSuggests(res)
            return

    if user.inQuiz:
        quiz = quizzes[user.quizId]
        if user.curQuestion < len(quiz['questions']) - 1:
            if 'STOP' in intents:
                exit_quiz(user)
                res['response']['text'] = random.choice(
                    phraseVariables['exit_from_quiz'])
                send_idleSuggests(res)
                return
            handle_quiz(req, res, user, 'REPEAT_QUESTION' not in intents)
            send_quizSuggests(res, user)
            return
        elif user.curQuestion == len(quiz['questions']) - 1:
            send_quizResult(req, res, user)
            return

    if not user.inQuiz:
        if user.justFinished:
            if 'YANDEX.REPEAT' in intents:
                res['response']['text'] = random.choice(
                    phraseVariables['repeat_quiz'])
                user.justFinished = False
                user.inQuiz = True
                send_idleSuggests(res)
                return
        if 'START_QUIZ' in intents:
            quiz = req.request.nlu.intents['START_QUIZ']['slots']['quiz_title']['value']
            res['response']['text'] = f'Вы захотели запустить викторину {quiz}'
            send_idleSuggests(res)
            return
        if 'SHOW_TOP' in intents:
            res['response']['text'] = random.choice(
                phraseVariables['show_top'])
            send_idleSuggests(res)
            return
        if 'START_RANDOM_QUIZ' in intents:
            preview_quiz(user, res, random.randint(0, len(quizzes) - 1))
            return
        if 'CREATE_QUIZ' in intents:
            res['response']['text'] = random.choice(
                phraseVariables['create_quiz'])
            send_idleSuggests(res)
            send_creationSuggest(res)
            return
        if 'WHAT_YOU_CAN_DO' in intents:
            res['response']['text'] = "Я могу запустить случайную или выбранную тобой викторину, \
могу вывести топ самых проходимых. А если ты не нашел той викторины, которую хотел пройти, \
можешь сам ее создать"
            send_idleSuggests(res)
            return
        if 'YANDEX.HELP' in intents:
            res['response']['text'] = "Викторины состоят из нескольких вопросов, в ответ на каждый ты\
можешь выбрать один вариант из нескольких предложенных. Ответив на каждый вопрос, ты узнаешь результат"
            send_idleSuggests(res)
            return
    if user.justFinished and 'REPEAT_QUIZ' in intents:
        preview_quiz(user, res, user.lastQuizId)
        return

    user.justFinished = False
    user.isNew = False
    send_error(res)
    if user.inQuiz:
        if user.curQuestion == -1:
            send_yesnoSuggest(res)
        else:
            send_quizSuggests(res, user)
    else:
        send_idleSuggests(res)


def handle_quiz(req: Req, res, user: User, next_=True):
    # Получение ответа
    if user.curQuestion != -1 and next_:
        if not check_quizAnswer(req, res, user):
            return

    # Следующий вопрос
    user.curQuestion += 1 if next_ else 0
    question = quizzes[user.quizId]['questions'][user.curQuestion]
    title = question['title']
    answers = [i['title'] for i in question['answers']]
    res['response']['text'] = title + "\n" + \
        "\n".join(f"{i}. {row}" for i, row in enumerate(answers, start=1))


def check_quizAnswer(req: Req, res, user: User):
    intents = req.request.nlu.intents
    quiz = quizzes[user.quizId]
    question = quiz['questions'][user.curQuestion]
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


def send_quizResult(req: Req, res, user: User):
    # Проверка последнего ответа
    check_quizAnswer(req, res, user)

    # Вывод результата
    quiz = quizzes[user.quizId]
    if quiz['type'] == 'person':
        result = max(user.result.items(), key=lambda x: x[1])[0]
        text = f'Ты - {result}'
        res['response']['text'] = text
        res['response']['card'] = {}

        character = [i for i in quiz['characters'] if i['name'] == result][0]
        card = res['response']['card']
        card['type'] = 'BigImage'
        card['title'] = text
        card['description'] = character['description']
        card['image_id'] = character['image']
    elif quiz['type'] == 'percent':
        result = round(
            user.result / len(quizzes[user.quizId]['questions']) * 100)
        res['response']['text'] = f'Ваш результат - {result}%. Вы можете пройти заново эту викторину или начать другую'

    send_idleSuggests(res)
    res['response']['buttons'] = [
        {
            "title": "Заново 🔁",
            "hide": True
        }
    ] + res['response']['buttons']

    # Выход из Виткторины
    user.lastQuizId = user.quizId
    user.inQuiz = False
    user.quizId = None
    user.curQuestion = None
    user.justFinished = True
    user.result = {}
    return


def preview_quiz(user: User, res, quiz_id):
    user.quizId = quiz_id
    user.previewQuiz = True

    # Превью
    title = quizzes[user.quizId]['title']
    description = quizzes[user.quizId]['description']
    creator = quizzes[user.quizId]['creator']
    preview = quizzes[user.quizId]['image']
    res['response']['text'] = f"{title}\n{description}\nСоздатель:{creator}\nНачинаем?"
    res['response']['card'] = {}
    card = res['response']['card']
    card['type'] = 'BigImage'
    card['image_id'] = preview
    card['title'] = f'{title} Начинаем?'
    card['description'] = f'{description}\nСоздатель: {creator}'
    send_yesnoSuggest(res)


def start_quiz(user: User):
    user.inQuiz = True
    user.curQuestion = 0
    quiz = quizzes[user.quizId]
    if quiz['type'] == 'person':

        user.result = {character['name']: 0 for character in quiz['characters']}
    elif quiz['type'] == 'percent':
        user.result = 0


def exit_quiz(user: User):
    user.quizId = None
    user.curQuestion = None
    user.inQuiz = False
    user.justFinished = False
    user.result = {}


def send_idleSuggests(res):
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


def send_quizSuggests(res, user: User):
    answers = len(quizzes[user.quizId]['questions']
                  [user.curQuestion]['answers'])
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


def send_yesnoSuggest(res):
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


def send_error(res):
    res['response']['text'] = "Извини, я не поняла, повтори пожалуйста"


def download_image_by_bits(image_bits):
    alice_url = 'https://dialogs.yandex.net/api/v1/skills/a9331dba-12d5-41be-ba3b-d691a6294153/images'
    headers = {
        'Authorization': 'OAuth y0_AgAAAAAhKRZBAAT7owAAAADfkTMUOctm8BgkQU-3pQ8X_Vd5UK3G1qw'}
    files = {'file': image_bits}
    req = requests_lib.post(url=alice_url, headers=headers, files=files)
    return req.json()


def delete_image(image_id):
    alice_url = f'https://dialogs.yandex.net/api/v1/skills/a9331dba-12d5-41be-ba3b-d691a6294153/images/{image_id}'
    headers = {
        'Authorization': 'OAuth y0_AgAAAAAhKRZBAAT7owAAAADfkTMUOctm8BgkQU-3pQ8X_Vd5UK3G1qw'}
    req = requests_lib.delete(url=alice_url, headers=headers)
    return req.json()