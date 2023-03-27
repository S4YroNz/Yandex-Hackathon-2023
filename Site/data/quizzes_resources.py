from flask_restful import abort, Resource
from flask import jsonify

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
        session = db_session.create_session()
        quiz = session.query(Quiz).all()
        return jsonify({'quiz': [item.to_dict(
            only=('title', ...)) for item in quiz]})  # оставляем нужные параметры

    def post(self):
        args = parser_quiz.parse_args()
        session = db_session.create_session()
        quiz = Quiz(
            title=args['title'],
        )  # оставляем нужные параметры
        session.add(quiz)
        session.commit()
        return jsonify({'success': 'OK'})
