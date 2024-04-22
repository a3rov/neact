import sqlalchemy as db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = db.create_engine('sqlite:///data/database.db')


Base = declarative_base()


class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(320))
    username = Column(String(32))
    password = Column(String())
    profile_description = Column(String(64))
    regdate = Column(String())
    link_type = Column(String(16))
    link = Column(String())


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    unique = Column(String())
    title = Column(String(64))
    description = Column(String(128))
    price = Column(Integer())
    status = Column(String())
    author = Column(Integer())
    author_username = Column(String())
    date = Column(String())
    creator = Column(Integer())


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    text = Column(String(1024))
    receiver = Column(Integer())
    author = Column(Integer())
    date = Column(String())


class Feedback(Base):
    __tablename__ = 'feedbacks'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer())
    author = Column(Integer())


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer())
    creator = Column(Integer())
    author = Column(Integer())
    author_username = Column(String())
    rate = Column(Integer())
    text = Column(String())


Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
sql_session = Session()
