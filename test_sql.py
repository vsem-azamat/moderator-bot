from db.sql_aclhemy import db
from db.alchemy_decl import Users, Chats

# q = db.s.query(Users.verify, Users.black_list).filter(Users.id_tg==12345).first()


# welc = db.welcome_message(12345)
welc = db.s.query(Chats.text, Chats.time_delete, Chats.state_func, Chats.state_text).filter(Chats.id_tg_chat==12345)

# print(welc)


for i in welc:
    print(dict(i))

# for i in welc:
#     print(i)


# user = db.check_user(12345)
# print(user)