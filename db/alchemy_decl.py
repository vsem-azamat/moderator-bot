from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# engine = create_engine('sqlite:///db/moder_bot.db')
Base = declarative_base()


class Total_Admins(Base):
    __tablename__ = 'total_admins'

    id = Column(Integer, primary_key=True)
    id_tg = Column(Integer, nullable=False)
    state = Column(Boolean, default=True)
    

class Admins(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    id_tg = Column(Integer, nullable=False)
    state = Column(Boolean, default=True)           #global state of admin


class Chats(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True)
    id_tg_chats = Column(Integer, nullable=False)
    text = Column(Text)
    time_delete = Column(Integer, default=60)       # time for autodelete welcome message
    state_func = Column(Boolean, default=False)     # state of on/off welcome MESSAGE
    state_test = Column(Boolean, default=False)     # state of on/off welcome TEST

class Chat_Admins(Base):
    __tablename__ = 'chat_admins'

    id = Column(Integer, primary_key=True)
    id_chat = Column(Integer, ForeignKey('chats.id'))
    id_admins = Column(Integer, ForeignKey('admins.id'))
    state = Column(Boolean, default=True)
    
    chats = relationship('Chats')
    admins = relationship('Admins')


class Commands(Base):
    __tablename__ = 'commands'

    id = Column(Integer, primary_key=True)
    command = Column(Text, unique=True)


class Command_States(Base):
    __tablename__ = 'command_states'

    id = Column(Integer, primary_key=True)
    id_command = Column(Integer, ForeignKey('commands.id'))
    id_chat = Column(Integer, ForeignKey('chats.id'))
    state =Column(Boolean, default=True)

    commands = relationship('Commands')
    chats = relationship('Chats')


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    id_tg = Column(Integer, nullable=False)
    verify = Column(Boolean, default=True)
    q_respect = Column(Integer, default=0)
    q_wanr = Column(Integer, default=0)


class Black_List(Base):
    __tablename__ = 'black_list'

    id = Column(Integer, primary_key=True)
    id_tg = Column(Integer, nullable=False)
    

