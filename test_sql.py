from db.sql_aclhemy import db
from db.alchemy_decl import Users, Chats

id = 12345
message = "!welcome -b"
param = message.partition(" ")[2]

t = db.welcome_command(id, param)
print(t)

q = db.s.query(Chats.state_func, Chats.state_test).filter(Chats.id_tg_chat == id).first()
print(q)
