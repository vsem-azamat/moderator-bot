import datetime
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
        
        *is empty if user doesnt exist in the DB
        """
        q = self.s.query(Users.black_list, Users.verify).filter(Users.id_tg == id_tg)
        return self.conv_dict(q) if self.check_exists(id_tg) else {}


    def check_verify(self, id_tg:int) -> bool:
        """
        Checks the "verify" status of the User
        """
        return self.s.query(Users.verify).filter(Users.id_tg == id_tg).first()[0]
        

    def change_verify(self, id_tg:int, state:bool) -> None:
        request = update(Users).where(id_tg==id_tg).values(verify=state)
        self.engine.execute(request)


    def welcome_test(self, id_tg_chats:int):
        dates = self.s.query(Chats.state_func).filter(Chats.id_tg_chat==id_tg_chat)[0][0]
        return self.conv_dict(dates)


    def welcome_message(self, id_tg_chat:int):    
        """
        return -> dict:
        {'text':          Welcome text}
        {'time_delete':   Auto-delete time message}
        {'state_text':    State of welcome message}
        {'state_func':    State of welcome test}
        """
        q = self.s.query(Chats.text, Chats.time_delete, Chats.state_func, Chats.state_text).filter(Chats.id_tg_chat==id_tg_chat)
        # if q:
        #     return self.conv_dict(q)
        # else:
        #     f = open('texts/welcome.txt', encoding='utf-8', mode='r').read()
        #     welcome = Chats(id_tg_chat=id_tg_chat, text=f)
        return q.first()
        # return self.conv_dict(q) if q.first() else {}

    def add_new_user(self, id_tg:int, state_func:bool = True):
        """
        Add the user to the DB if it doesnt exist
        """
        if self.check_exists(id_tg) == False:
            user = Users(id_tg=id_tg, state_verify={False:True,False:True}[state_func])
            self.s.add(user)
            self.s.commit()
        

db = SqlAlchemy()

# black = Black_List(id_tg = 12345)
# db.s.add(black)


# q = db.check_user(2165)
# print(q)