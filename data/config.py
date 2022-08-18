import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv('TOKEN'))

SUPER_ADMINS = [int(id_admin) for id_admin in os.getenv('ADMINS').split(',')]
