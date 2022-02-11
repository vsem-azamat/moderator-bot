from datetime import datetime

#types of dates
from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, Boolean, ForeignKey

metadata = MetaData()
# main admins
total_admins = Table('total_admins', metadata,
    Column('id', Integer, primary_key=True),
    Column('id_tg', Integer),
    Column('state', Boolean, default=False)
)

# local admins in chats and they global states
admins = Table('admins', metadata,
    Column('id', Integer(), primary_key=True),
    Column('id_tg', Integer()),
    Column('state', Boolean(), default=True)        # global state of admin 
)

chats = Table('chats', metadata,
    Column('id', Integer(), primary_key=True),
    Column('id_tg_chats', Integer(), nullable=False),
    Column('text', Text()),
    Column('time_delete', Integer(), default=60),   # time for autodelete welcome message
    Column('state_text', Boolean(), default=False), # state for on/off welcome TEST
    Column('state_test', Boolean(), default=False)  # state for on/off welcome TEXT
)

chat_admins = Table('chat_admins', metadata,
    Column('id', Integer(), primary_key=True),
    Column('id_chat', Integer(), ForeignKey('chats.id')),
    Column('id_admins', Integer(), ForeignKey('admins.id')),
    Column('state', Boolean(), default=True)           # state of admin on local chat
)

commands = Table('commands', metadata,
    Column('id', Integer(), primary_key=True),
    Column('command', Text(), unique=True)
)

command_states = Table('command_states', metadata,
    Column('id', Integer(), primary_key=True),
    Column('id_command', Integer(), ForeignKey('commands.id')),
    Column('id_chat', Integer(), ForeignKey('chats.id')),
    Column('state', Boolean(), default=True)
)

users = Table('users', metadata,
    Column('id', Integer(), primary_key=True),
    Column('id_tg', Integer()),
    Column('verify', Boolean(), default=True),
    Column('q_respect', Integer(), default=0),
    Column('q_warn', Integer(), default=0)
)

# Black list of users
black_list = Table('black_list', metadata,
    Column('id', Integer(), primary_key=True),
    Column('id_user', Integer(), ForeignKey('users.id'))
)