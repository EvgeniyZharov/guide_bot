from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data_clients.MySQLClient import DataClient
from languages.languages import languages

from config import MAIN_TOKEN


data_client = DataClient()
data_client.create_db()

"""
AgACAgIAAxkBAAIO_2XgoY-fHE7mQ4SjzEJm59XooLsLAALT1zEbyMYAAUuOiUQ1x3xrvwEAAwIAA3kAAzQE

"""





# print(data_client.get_random_ask(quiz_id=14, ask_id_ready=[37, 38]))
storage = MemoryStorage()

bot = Bot(token=MAIN_TOKEN)
dp = Dispatcher(bot, storage=storage)