from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# engine = create_engine('sqlite:///db/moder_bot.db')
Base = declarative_base()


class Admins(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    id_tg = Column(Integer, nullable=False)
    state = Column(Boolean, default=True)           #global state of admin


class Chats(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True)
    id_tg_chat = Column(Integer, nullable=False)
    text = Column(Text)
    time_delete = Column(Integer, default=60)       # time for autodelete welcome message
    state_func = Column(Boolean, default=False)     # state of on/off welcome MESSAGE
    state_test = Column(Boolean, default=False)     # state of on/off welcome TEST
    db_admins = Column(Integer, default=True)


class Commands(Base):
    __tablename__ = 'commands'

    id = Column(Integer, primary_key=True)
    command = Column(Text, unique=True)
    state = Column(Boolean, default=True)


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    id_tg = Column(Integer, nullable=False)
    verify = Column(Boolean, default=True)
    q_respect = Column(Integer, default=0)
    q_warn = Column(Integer, default=0)
    black_list = Column(Boolean, default=False)
