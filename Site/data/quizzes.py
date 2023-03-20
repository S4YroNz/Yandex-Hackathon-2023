import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Quiz(SqlAlchemyBase):
    __tablename__ = 'quiz'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    creator = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    questions = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # строка в формате json

    user = orm.relationship('User')
