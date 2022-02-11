import datetime
import sqlalchemy 
from sqlalchemy import create_engine, select, insert
from sqlalchemy.orm import sessionmaker

from alchemy_decl import Total_Admins, Admins, Base, Chat_Admins, Commands, Command_States, Users, Black_List, Chats


class SqlAlchemy():
    def __init__(self):
        self.engine = create_engine('sqlite:///db/moder_bot.db')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        self.s = self.session()
        
        self.conn = self.engine.connect()
    
    def conv_dict(self, query):
        for i in query:
            query = dict(i)
        return query
    

    def execute(self, sql):
        return self.conn.execute(sql)

    
    def black_list(self, id_tg):
        return self.s.query(Black_List.id_tg).filter(Black_List.id_tg == id_tg)[0][0]
            
        
    def welcome_message(self, id_tg: int, id_chat: int):    
        query = self.s.query(Chats.text, Chats.time_delete, Chats.state_test, Chats.state_text).filter(Chats.id_tg_chats == id_chat)   
        return self.conv_dict(query)
        

    def enter_in_chat(self, id_tg: int):
        if self.s.query(Users.id).filter(User.id_tg == id_tg)[0][0] is None:
            user = User(id_tg = id_tg)     # решить вопрос с verify
            self.s.add(user)
            self.s.commit()



db = SqlAlchemy()

res = db.s.query(Chats.id, Chats.text).filter(Chats.id == 1)

print(f"Test: {res[0]}")

# for i in res:
#     print(i)


# res = db.welcome_message(12345, 12345)
# print(res)


# for i in res:
#     print(dict(i))


# chat = Chats(id_tg_chats = 12345, text = 'test')
# db.s.add(chat)
# db.s.commit()