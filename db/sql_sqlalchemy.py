from datetime import datetime

import sqlalchemy 
from sqlalchemy import create_engine, select
from sqlalchemy.sql import exists

#types of dates
from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, Boolean, ForeignKey

metadata = MetaData()
# main admins
total_admins = Table('total_admins', metadata,
    Column('id', Integer, primary_key=True),
    Column('id_tg', Integer),
    Column('state', Boolean)
)

# local admins in chats and they global states
admins = Table('admins', metadata,
    Column('id', Integer(), primary_key=True),
    Column('id_tg', Integer()),
    Column('state', Boolean())
)

chats = Table('chats', metadata,
    Column('id', Integer(), primary_key=True),
    Column('id_tg_chats', Integer(), nullable=False)
)

chat_admins = Table('chat_admins', metadata,
    Column('id', Integer(), primary_key=True),
    Column('id_chat', Integer(), ForeignKey('chats.id')),
    Column('id_admins', Integer(), ForeignKey('admins.id')),
    Column('state', Boolean())
)

welcome_test = Table('welcome_test', metadata,
    Column('id', Integer(), primary_key=True),
    Column('id_chat', Integer(), ForeignKey('chats.id')),
    Column('text', Text()),
    Column('time_autodele', Integer()),
    Column('state_text', Boolean()),
    Column('state_test', Boolean())
)

commands = Table('commands', metadata,
    Column('id', Integer()),
    Column('command', Text())
)

command_states = Table('command_states', metadata,
    Column('id', Integer(), primary_key=True),
    Column('id_command', Integer(), ForeignKey('command.id')),
    Column('id_chat', Integer(), ForeignKey('chats.id')),
    Column('state', Boolean())
)

users = Table('users', metadata,
    Column('id', Integer(), primary_key=True),
    Column('id_tg', Integer()),
    Column('verify', Boolean()),
    Column('q_respect', Integer()),
    Column('q_warn', Integer())
)

black_list = Table('black_list', metadata,
    Column('id', Integer(), primary_key=True),
    Column('id_user', Integer(), ForeignKey('users.id'))
)

class SqlAlchemy():
    def __init__(self):
        self.engine = create_engine('sqlite:///db/moder_bot.db')
        self.conn = self.engine.connect()


    def execute(self, sql):
        return self.conn.execute(sql)


    def check_exists(self, id_row:int, table:str='users', where_column:str='id_tg', return_column:tuple = ('id', 'id_tg')):
        """
        row  exists -> id_tg
        dont exists -> 0
        """
        sql = f"SELECT {', '.join(return_column)} FROM {table} WHERE {where_column} = {id_row};"
        return execute(sql).black_list.fetchone()


    def welcome_test(self, id_chat: int):
        row = check_exists(id_chat, 'chats', 'id_chats', ('text', 'time_delete_text', 'state_test', 'state_text')).fetchone() 
        if row[-1] and row[-2]: #text and test -> text with test
            pass
        elif row[-1] and not row[-2]: #text and not test -> only text
            pass
        #запихать логику в хендлер#

    def enter_in_chat(self, id_tg: int):
        if not check_exists(id_tg):
            self.execute(users.insert().values(id_tg))

        elif check_exists(id_tg, 'black_list'):
            "block user"
            return 1


db = SqlAlchemy()

res = db.check_exists(1, return_column = ['id_tg', 'state'], where_column='id', table='admins')
print(res)
