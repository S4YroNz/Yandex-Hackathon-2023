from flask_restful import reqparse

parser_quiz = reqparse.RequestParser()
parser_quiz.add_argument('id', required=True)
parser_quiz.add_argument('owner_id', required=True)
parser_quiz.add_argument('title', required=True)
parser_quiz.add_argument('json', required=True)

parser_user = reqparse.RequestParser()
parser_user.add_argument('id', required=True)
