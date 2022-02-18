import datetime
import sqlalchemy 
from sqlalchemy import create_engine, select, insert, update
from sqlalchemy.orm import sessionmaker

from .alchemy_decl import Total_Admins, Admins, Base, Chat_Admins, Commands, Command_States, Users, Black_List, Chats

class SqlAlchemy():
    def __init__(self):
        self.engine = create_engine('sqlite:///db/moder_bot.db')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        self.s = self.session()
        
        self.conn = self.engine.connect()
    
    # convert result of query to dict
    def conv_dict(self, query):
        for i in query:
            query = dict(i)
        return query
    
    def check_exists(self, id_tg):
        return self.s.query(Users.id).filter(Users.id_tg==id_tg).first()[0]


    def execute(self, sql):
        return self.conn.execute(sql)        

    
    def check_black_list(self, id_tg:int):
        return self.s.query(Black_List.id_tg).filter(Black_List.id_tg == id_tg)[0][0]
            
    
    def check_verify(self, id_tg:int) -> bool:
        return self.s.query(Users.verify).filter(Users.id_tg == id_tg).first()[0]
        

    def change_verify(self, id_tg:int, state:bool):
        request = update(Users).where(id_tg==id_tg).values(verify=state)
        self.engine.execute(request)


    def welcome_test(self, id_tg_chats:int):
        dates = self.s.query(Chats.state_test).filter(Black_List.id_tg == id_tg_chats)[0][0]
        return self.conv_dict(dates)


    def welcome_message(self, id_tg_chat:int):    
        """
        Reurns -> [dict,]:
        {'text':          Welcome text}
        {'time_delete':   Time autodelete message}
        {'state_func':    State of welcome message}
        {'state_test':    State of welcome message}
        """
        # dates = self.s.query(Chats.text, Chats.time_delete, Chats.state_func, Chats.state_test).filter(Chats.id_tg_chats == id_tg_chat)   
        # return self.conv_dict(dates)
        return self.s.query(Chats).get(1)


    def new_chat_member(self, id_tg:int, state_func:bool = True):
        if self.check_exists(id_tg) == False:
            user = Users(id_tg=id_tg, state_verify={False:True,False:True}[state_func])
            self.s.add(user)
            self.s.commit()
        

db = SqlAlchemy()
