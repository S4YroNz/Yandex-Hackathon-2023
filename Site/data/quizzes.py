import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Quiz(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'quiz'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    views = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    user = orm.relationship('User')
