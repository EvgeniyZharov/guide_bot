from aiogram import types
from initial import bot, dp
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from initial import DataClient
from handlers.admin import LandmarkSettings
from handlers.admin import QuizSettings

from keyboards import create_keyboards
from config import FSMWorkProgram


class AdminClient:
    btn_admin_main_menu = ["Виртуальный Гид",
                           "Викторины",
                           "О проекте",
                           "Системные настройки"]
    btn_settings = ["Виртуальный гид",
                    "Квиз",
                    "Достопримечательности"]

    def __init__(self, data_client: DataClient):
        self.data_client = data_client
        self.LandmarkSettings = LandmarkSettings.LandmarkSettings(data_client=data_client)
        self.QuizSettings = QuizSettings.QuizSettings(data_client=data_client)

    async def start_admin_main_menu(self, msg: types.Message):
        await msg.answer("Привет, администратор!",
                         reply_markup=create_keyboards(self.btn_admin_main_menu))
        await FSMWorkProgram.admin_main_menu.set()

    async def settings(self, msg: types.Message):
        await msg.answer("Выберите, какой режим планируете настроить.",
                         reply_markup=create_keyboards(self.btn_settings))
        await FSMWorkProgram.admin_settings.set()

    def run_handler(self):
        dp.register_message_handler(self.start_admin_main_menu,
                                    Text(equals="Перейти", ignore_case=True),
                                    state=FSMWorkProgram.to_admin_main_menu)
        dp.register_message_handler(self.settings,
                                    Text(equals="Системные настройки", ignore_case=True),
                                    state=FSMWorkProgram.admin_main_menu)

        self.LandmarkSettings.run_handler()
        self.QuizSettings.run_handler()

