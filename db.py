from typing import Any
import exceptions

from sqlalchemy import Boolean, Text, create_engine, DateTime
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils import database_exists, create_database
from local_settings import psql

from dateutil.relativedelta import relativedelta

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    userid = Column(Integer)
    text = Column(String)
    datetime = Column(DateTime)
    repeat = Column(Boolean)

    def __repr__(self):
        return f"<Task(id={self.id}, userid={self.userid}, text={self.text}, time={self.datetime}, repeat={self.repeat})>"


def get_engine():
    url = f"postgresql://{psql['pguser']}:{psql['pgpasswd']}@{psql['pghost']}:{psql['pgport']}/{psql['pgdb']}"
    if not database_exists(url):
        create_database(url)
    return create_engine(url,pool_size=50, echo=False)


def get_session():
    engine =get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def taskExists(func):
    def wrapper(*args, **kwargs):
        session = get_session()
        task = session.query(Task).filter(Task.id == args[0]).first()
        session.close()
        if task is None:
            raise exceptions.TaskNotExist
        else:
            return func(*args, **kwargs)
    
    return wrapper


def add_task(Message: Any) -> str:
    
    session = get_session()

    task = Task(userid=Message.user_id, text=Message.text, datetime=Message.datetime, repeat=Message.repeat_flag)
    session.add(task)
    session.commit()
    session.close()

@taskExists
def get_task(taskID:int) -> Task:
    session = get_session()
    taskOB = session.query(Task).filter(Task.id == taskID).first()
    session.close()
    return taskOB

@taskExists
def edit_task(taskID:int, **kwargs:dict) -> Task:
    session = get_session()
    task = session.query(Task).filter(Task.id == taskID).first()
    for key, value in kwargs.items():
        setattr(task, key, value)
    session.commit()
    session.close()
    return get_task(taskID)

@taskExists
def delete_task(taskID:int):
    session = get_session()
    task = session.query(Task).filter(Task.id == taskID).first()
    session.delete(task)
    session.commit()
    session.close()

def get_tasks(userid:int) -> list:
    session = get_session()
    tasks = session.query(Task).filter(Task.userid == userid).all()
    session.close()
    return tasks

def get_NearTask() -> Task:
    session = get_session()
    tasks = session.query(Task).order_by(Task.datetime).all()
    if len(tasks) == 0:
        session.close()
        raise exceptions.TasksListIsEmpty
    session.close()
    return min(tasks ,key=lambda x: x.datetime)


        
