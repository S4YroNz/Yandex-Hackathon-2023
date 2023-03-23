from flask_restful import reqparse

parser_quiz = reqparse.RequestParser()
parser_quiz.add_argument('title', required=True)
# Добавляем все параметры

parser_user = reqparse.RequestParser()
parser_user.add_argument('id', required=True)
parser_user.add_argument('email', required=True, type=bool)
# Добавляем все параметры
