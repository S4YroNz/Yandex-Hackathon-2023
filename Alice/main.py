import random
import requests
import json
import Levenshtein
import base64


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
        self.downloaded_images = r.get('downloaded_images', [])

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
    # if user.downloaded_images:
    #     for img_id in user.downloaded_images:
    #         delete_image(img_id)
    #     user.downloaded_images = []
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
            handle_quiz(req, res, user, quizzes[user.quiz_id], False)
            send_quiz_suggests(res, user, quizzes[user.quiz_id])
            return
        elif 'YANDEX.REJECT' in intents:
            exit_quiz(user)
            res['response']['text'] = random.choice(
                phraseVariables['exit_from_quiz'])
            send_idle_suggests(res)
            return

    if user.in_quiz:
        quiz = quizzes[user.quiz_id]
        print(
            f'BEFORE: {user.cur_question=} {quiz["questions"][user.cur_question]["title"]=}')
        if user.cur_question < len(quiz['questions']):
            if 'STOP' in intents:
                exit_quiz(user)
                res['response']['text'] = random.choice(
                    phraseVariables['exit_from_quiz'])
                send_idle_suggests(res)
                return
            if handle_quiz(req, res, user, quiz, 'REPEAT_QUESTION' not in intents):
                send_quiz_suggests(res, user, quiz)
                return
        if user.cur_question == len(quiz['questions']):
            send_quiz_result(req, res, user, quiz)
            return

    if 'YANDEX.HELP' in intents:
        res['response']['text'] = "Викторины состоят из нескольких вопросов, в ответ на каждый ты\
можешь выбрать один вариант из нескольких предложенных. Ответив на каждый вопрос, ты узнаешь результат"
        user.preview_quiz = False
        if user.in_quiz:
            send_quiz_suggests(res, user, quizzes[user.quiz_id])
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
            finded_quizz = find_quiz(
                intents['START_QUIZ']['slots']['quiz_title']['value'], [i['title'] for i in quizzes])[0]
            id_ = [i['id'] for i in quizzes if i['title'] == finded_quizz][0]
            preview_quiz(user, res, id_)
            return
        if 'SHOW_TOP' in intents:
            user.preview_quiz = False
            send_top(res)
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

        if 'STOP' in intents:
            res['response']['text'] = 'До встречи в следующий раз!'
            res['response']['end_session'] = True
            return

    if user.just_finished and 'REPEAT_QUIZ' in intents:
        preview_quiz(user, res, user.lastquiz_id)
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
            send_quiz_suggests(res, user, quizzes[user.quiz_id])
    else:
        send_idle_suggests(res)


def send_top(res):
    top = list(sorted(quizzes, key=lambda x: -x["views"]))[:5]
    res['response']['text'] = f'''{top[0]["title"]}\n
                    {top[1]["title"]}\n
                    {top[2]["title"]}\n
                    {top[3]["title"]}\n
                    {top[4]["title"]}\n'''
    res['response']['card'] = {
        'type': 'ItemsList',
        'header':
            {
                'text': 'Топ викторин'
            },
        'items': [{
            'title': f'{i}) {top_title["title"]}',
            'button':
            {
                'text': f'Запусти викторину {top_title["title"]}'
            }
        } for i, top_title in enumerate(top, start=1)]
    }


def find_quiz(user_req, all_titles, delta_distance=6):
    symb = '.,/!?@"№;:<>#$%^&*()\|=+-_1234567890'
    user_req = str(user_req)
    for let in symb:
        user_req = user_req.replace(let, '')
    user_req = user_req.lower()

    re = []
    for i in range(len(all_titles)):
        el = all_titles[i]
        for let in symb:
            el = el.replace(let, '')
        el = el.lower()
        re.append([all_titles[i], Levenshtein.distance(user_req, el)])

    re = list(sorted(re, key=lambda x: x[1]))
    ans = []
    ans.append(re[0][0])
    min_distance = re[0][1]
    try:
        if re[1][1] - min_distance < delta_distance:
            ans.append(re[1][0])
        if re[2][1] - min_distance < delta_distance:
            ans.append(re[2][0])
    except Exception:
        pass
    return ans


def send_answers(res, title, answers):
    card = {
        'type': 'ItemsList',
        'header':
        {
            'text': title
        },
        'items': [
            {

                'title': f'{i}) {answer_title}'
            }
            for i, answer_title in enumerate(answers, start=1)]
    }
    res['response']['card'] = card
    text = '.'.join(answers)
    res['response']['tts'] = text
    res['response']['text'] = text


def handle_quiz(req, res, user: User, quiz, next_=True):
    # Получение ответа
    if user.cur_question != -1 and next_:
        if not check_quiz_answer(req, res, user, quiz):
            return True

    # Следующий вопрос
    user.cur_question += 1 if next_ else 0
    if user.cur_question == len(quiz['questions']):
        return False
    question = quiz['questions'][user.cur_question]
    title = question['title']
    answers = [i['title'] for i in question['answers']]
    send_answers(res, title, answers)
    return True


def check_quiz_answer(req, res, user: User, quiz):
    intents = req['request']['nlu']['intents']
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
        user.result[answers[user_answer - 1]['character']] += 1
    elif quiz['type'] == 'percent':
        correct = [i for i, a in enumerate(
            question['answers'], start=1) if a['is_true']][0]
        if user_answer == correct:
            user.result += 1
    return True


def send_quiz_result(req, res, user: User, quiz):
    if quiz['type'] == 'person':
        result = max(user.result.items(), key=lambda x: x[1])[0]
        character = [i for i in quiz['characters'] if i['name'] == result][0]
        text = f'Ты - {result}. {character["description"]}'
        res['response']['text'] = text
        if character['image']:
            res['response']['card'] = {}
            card = res['response']['card']
            card['type'] = 'BigImage'
            card['title'] = text
            card['description'] = character['description']
            # character_image_id = upload_image(base64.decodebytes(
            #     character['image'].encode('utf-8')))['id']
            # user.downloaded_images.append(character_image_id)
            # card['image_id'] = character_image_id
            card['image_id'] = character['image']
    elif quiz['type'] == 'percent':
        result = round(user.result / len(quiz['questions']) * 100)
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


# def get_quiz(id_):
#     return requests.get(f'https://yaquizserver.onrender.com/api/quiz/{id_}').json()


def preview_quiz(user: User, res, quiz_id):
    user.quiz_id = quiz_id
    user.preview_quiz = True

    # Превью
    quiz = quizzes[user.quiz_id]
    title = quiz['title']
    description = quiz['description']
    creator = quiz['creator']
    preview = quiz['image']
    res['response']['text'] = f"{title}\n{description}\nСоздатель: {creator}. \nНачинаем?"
    if quiz['image']:
        res['response']['card'] = {}
        card = res['response']['card']
        card['type'] = 'BigImage'
#         title_image_id = upload_image(base64.decodebytes(\
# preview.encode('utf-8')))['image']['id']
#         user.downloaded_images.append(title_image_id)
#         card['image_id'] = title_image_id
        card['image_id'] = preview
        card['title'] = f'{title}'
        card['description'] = f'{description}\nСоздатель: {creator}. \nНачинаем?'
    send_yesno_suggest(res)


def start_quiz(user: User):
    user.in_quiz = True
    user.cur_question = 0
    quiz = quizzes[user.quiz_id]
    if quiz['type'] == 'person':
        user.result = {
            character['name']: 0 for character in quiz['characters']
        }
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


def send_quiz_suggests(res, user: User, quiz):
    answers = len(quiz['questions']
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
            "title": "Создать викторину",
            "url": "https://yaquizserver.onrender.com/",
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
    res['response']['text'] = random.choice(
        phraseVariables['error'])


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
