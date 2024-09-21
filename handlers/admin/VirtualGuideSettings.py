from aiogram import types
from initial import bot, dp
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from initial import DataClient

from keyboards import create_keyboards
from config import FSMWorkProgram


class VirtualGuideSettings:
    def __init__(self, data_client: DataClient):
        self.data_client = data_client

    # async def
    #
    # def run_handler(self):
    #     dp.register_message_handler(self.start_admin_main_menu,
    #                                 Text(equals="Перейти", ignore_case=True),
    #                                 state=FSMWorkProgram.to_admin_main_menu)