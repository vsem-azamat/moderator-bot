import re
import datetime
from aiogram import types

import sqlalchemy 
from sqlalchemy import create_engine, select, insert, update
from sqlalchemy.orm import sessionmaker

from .alchemy_decl import Total_Admins, Admins, Base, Chat_Admins, Commands, Command_States, Users, Chats


class SqlAlchemy():
    def __init__(self):
        self.engine = create_engine('sqlite:///db/moder_bot.db')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        self.s = self.session()
        
        self.conn = self.engine.connect()
    

    def conv_dict(self, query) -> dict:
        """
        Converts the query result to a dict
        """
        return [dict(i) for i in query][0]

    def check_exists(self, id_tg):
        return True if self.s.query(Users).filter(Users.id_tg==id_tg).first() else False

    def execute(self, sql):
        return self.conn.execute(sql)        

    
    def check_user(self, id_tg:int) -> dict:
        """
        return -> dict
            keys: black_list, verify

        *return will be empty dict, if user doesnt exist in the DB
        """
        q = self.s.query(Users.black_list, Users.verify).filter(Users.id_tg == id_tg)
        return self.conv_dict(q) if self.check_exists(id_tg) else {}


    def check_verify(self, id_tg:int) -> bool:
        """
        Checks the "verify" status of the User
        """
        return self.s.query(Users.verify).filter(Users.id_tg == id_tg).first()[0]
        

    def change_verify(self, id_tg:int, state:bool) -> None:
        """
        Changes the verify status of the User
        """
        request = update(Users).where(Users.id_tg==id_tg).values(verify=state)
        self.engine.execute(request)


    def welcome_test(self, id_tg_chats:int):
        dates = self.s.query(Chats.state_func).filter(Chats.id_tg_chat==id_tg_chat)[0][0]
        return self.conv_dict(dates)


    def welcome_message(self, id_tg_chat:int, return_:bool=True):    
        """
        return -> dict:
        {'text':          Welcome text}
        {'time_delete':   Auto-delete time message}
        {'state_text':    State of welcome message}
        {'state_func':    State of welcome test}

        If chat doesnt exist in the DB, 
        to will be created new row with text from "texts/welcome.txt"
        """
        q = self.s.query(Chats.text, Chats.time_delete, Chats.state_func, Chats.state_test).filter(Chats.id_tg_chat==id_tg_chat)
        if q.first() is None:
            f = open('texts/welcome.txt', encoding='utf-8', mode='r').read()
            welcome = Chats(id_tg_chat=id_tg_chat, text=f)
            self.s.add(welcome)
            self.s.commit()
        return self.conv_dict(q) if return_==True else None


    def welcome_command(self, id_tg_chat:int, param:str) -> str:
        """
        Work with table 'Chats'
        message params: 
             _: change state_func
        {text}: chande welcome text
            -t: change state_test
            -m: change message text
        """
        if len(param.split()) > 1:
            message = param.partition(" ")[2]
        param = param.split(" ")[0].strip()
        welc_info = self.welcome_message(id_tg_chat)

        # change state_func
        if param in ["", "on", "off"]:    
            value = {'On':True,'Off':False}.get(param,{True:False,False:True}[welc_info['state_func']])
            request = update(Chats).where(Chats.id_tg_chat==id_tg_chat).values(state_func=value)
            self.engine.execute(request)

            return "Приветствие %s!" % {True:'включено', False:'отключено'}[value]


        # change state_test
        elif param == '-b':
            value = {True:False,False:True}[welc_info['state_test']]            
            request = update(Chats).where(Chats.id_tg_chat==id_tg_chat).values(state_test=value)
            self.engine.execute(request)
            if welc_info['state_func'] is False:
                add_text = "\nНо приветствие в этом чате отключено."
            else:
                add_text = ""
            return f"Кнопка в приветствии %s!" % {True:'активирована', False:'деактивирована'}[value] + add_text


        elif param == '-t':
            try:
                value = int(message)
                if value >= 10 and value <= 900:
                    request = update(Chats).where(Chats.id_tg_chat==id_tg_chat).values(time_delete=value)
                    self.engine.execute(request)
                    return f"Время автоудаления приветствия установлено: {value} с."
                elif value >= 0 and value <= 10:
                    return "Минимальное время автоудаления 10 секунд."
                elif value >= 900:
                    return "Минимальное время автоудаления 900 секунд."
                else: 
                    raise ValueError
            except ValueError:
                return f"Вы некорректно задали параметр."
    
        # change message text
        else: 
            request = update(Chats).where(Chats.id_tg_chat==id_tg_chat).values(text=param)
            self.engine.execute(request)
            return f"<b>Приветствие отредактировано!<b> \n\n{param}"
     

    def add_new_user(self, id_tg:int, state_func:bool = True):
        """
        Add the user to the DB if it doesnt exist
        """
        if self.check_exists(id_tg) == False:
            state = {False:True,True:False}[state_func]
            user = Users(id_tg=id_tg, verify=state)
            self.s.add(user)
            self.s.commit()


    def mute_date(self, message:str) -> dict:        
        command_parse = re.compile(r"(!mute|/mute) ?(\d+)? ?(\b(m|h|d|w)\b)?")
        parsed = command_parse.match(message)
        time = parsed.group(2)
        unit = parsed.group(3)

        if unit is None:
            unit = 'm'

        if time is None:
            time = 5
        else:
            time = int(time)

        timedelta = {
            'm':datetime.timedelta(minutes=time),
            'h':datetime.timedelta(hours=time),
            'd':datetime.timedelta(days=time),
            'w':datetime.timedelta(weeks=time),
            None: datetime.timedelta(minutes=time)
            }.get(unit, datetime.timedelta(minutes=5))
            
        until_date = datetime.datetime.now() + timedelta

        print(time)
        print(unit)

        return {'until_date':until_date, 'time':time, 'unit':unit}


db = SqlAlchemy()

