from aiogram import types
from aiogram.utils import executor

from initial import dp, data_client

from handlers.user_client import UserClient

user_client = UserClient(data_client=data_client)

if __name__ == '__main__':
    user_client.run_handler()
    print("Program is run.")
    executor.start_polling(dp)
