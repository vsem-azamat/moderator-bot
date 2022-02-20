from db.alchemy_decl import *
from db.sql_aclhemy import db



user = Users(id_tg=12345)
welc = Chats(id_tg_chat=12345, text='Test')

db.s.add(user,welc)
db.s.commit()