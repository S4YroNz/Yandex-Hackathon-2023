from flask_restful import abort, Resource
from flask import jsonify
import json

from . import db_session
from .quizzes import Quiz
from .reqparse import parser_quiz


def abort_if_quiz_not_found(quiz_id):
    session = db_session.create_session()
    quiz = session.query(Quiz).get(quiz_id)
    if not quiz:
        abort(404, message=f"Quiz {quiz_id} not found")


class QuizResource(Resource):
    def get(self, quiz_id):
        abort_if_quiz_not_found(quiz_id)
        session = db_session.create_session()
        quiz = session.query(Quiz).get(quiz_id)
        with open(quiz.content_file) as file:
            return file
        #return jsonify({'quiz': quiz.to_dict(only=('id', 'title', 'description', 'creator', 'type', 'modified_date', ...))})   оставляем нужные параметры

    def delete(self, quiz_id):
        abort_if_quiz_not_found(quiz_id)
        session = db_session.create_session()
        quiz = session.query(Quiz).get(quiz_id)
        session.delete(quiz)
        session.commit()
        return jsonify({'success': 'OK'})


class QuizListResource(Resource):
    def get(self):
        # TODO: поиск всех файлом квизов в соответствующей папке
        files = ['quiz_1.json']
        json_file = {'quiz': []}
        for name in files:
            with open(name) as file:
                json_file['quiz'].append(json.load(file))
        return jsonify(json_file)

    def post(self):
        args = parser_quiz.parse_args()
        session = db_session.create_session()
        quiz = Quiz(
            title=args['title'],
        )  # оставляем нужные параметры
        session.add(quiz)
        session.commit()
        return jsonify({'success': 'OK'})
