import sqlalchemy
import datetime
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Quiz(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'quiz'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    creator = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # лучше bool
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content_file = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # название json-файла с персами и вопросами
    modified_date = sqlalchemy.Column(sqlalchemy.Date, nullable=True, default=datetime.date.today())

    user = orm.relationship('User')
