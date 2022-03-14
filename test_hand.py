from db.alchemy_decl import *
from db.sql_aclhemy import db
from sqlalchemy import select

s = "SELECT * FROM chats;"
q = db.execute(s)

t = ''

print(t)