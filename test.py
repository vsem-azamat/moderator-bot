import re

import datetime
import sqlalchemy 
from sqlalchemy import create_engine, select, insert, update
from sqlalchemy.orm import sessionmaker

# from .alchemy_decl import Total_Admins, Admins, Base, Chat_Admins, Commands, Command_States, Users, Chats


message = '!mute Как дела Всё хорошо!'
command_parse = re.compile(r"(!mute|/mute) ?(-\d+)? ?(\b(m|h|d|w)\b)? ?([\w+\D]+)?")
parsed = command_parse.match(message)

command = parsed.group(1)
time = parsed.group(2)
unit = parsed.group(3)
comment = parsed.group(5)

print(command)
print(time)
print(unit)
print(comment)