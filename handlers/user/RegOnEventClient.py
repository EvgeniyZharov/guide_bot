from aiogram import types
from initial import bot, dp
from keyboards import create_keyboards
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from random import shuffle

from initial import DataClient, languages


# from handlers.user.choice_place import
from config import FSMWorkProgram
# from handlers.user.choice_place_base import ChoicePlaceBase


class RegOnEventClient:
    # quiz_menu_btn = ["Статистика", "Играть"]

    def __init__(self, data_client: DataClient):
        self.data_client = data_client

    async def start_event_handler(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            user_lang = self.data_client.get_user_lang(user_id=str(msg.from_user.id))
            data["user_lang"] = user_lang
            # Выберите категорию мероприятия
            btn = self.data_client.get_event_type_btn(language=user_lang)
            await msg.answer(languages[user_lang]["start_event_reg"],
                             reply_markup=create_keyboards(btn, cancel_btn=True,
                                                           user_lang=user_lang))
            await FSMWorkProgram.event_main_menu.set()

    async def choice_event(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            event_type_id = self.data_client.get_event_type_id(title=msg.text)
            data["event_type_title"] = msg.text
            data["event_type_id"] = event_type_id
            # Выберите мероприятие
            btn = self.data_client.get_event_btn(event_type_id=event_type_id, language=data["user_lang"], town_id=1)
            await msg.answer(languages[data["user_lang"]]["choice_event"],
                             reply_markup=create_keyboards(btn, cancel_btn=True,
                                                           user_lang=data["user_lang"]))
            await FSMWorkProgram.choice_event.set()

    async def reg_on_event(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            event_id = self.data_client.get_event_id(title=msg.text, event_type_id=data["event_type_id"],
                                                     language=data["user_lang"])
            data["event_title"] = msg.text
            data["event_id"] = event_id
            # Хотите зарегистрироваться на это мероприятие?
        await msg.answer(languages[data["user_lang"]]["reg_on_event"],
                         reply_markup=create_keyboards(list(), cancel_btn=True, yes_no_btn=True,
                                                       user_lang=data["user_lang"]))
        await FSMWorkProgram.reg_on_event.set()

    async def save_reg(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if msg.text in languages["to_all"]["no"]:
                await msg.answer(languages[data["user_lang"]]["changes_unsaved"],
                                 reply_markup=create_keyboards(list()))
            if msg.text in languages["to_all"]["yes"]:
                user_id = self.data_client.get_user_id(user_id=f"{msg.from_user.id}")
                result = self.data_client.set_new_participant(group_id=1,
                                                              user_id=user_id,
                                                              language=data["user_lang"])
                if result:
                    await msg.answer(languages[data["user_lang"]]["changes_saved"],
                                     reply_markup=create_keyboards(list()))
                else:
                    await msg.answer(languages[data["user_lang"]]["changes_unsaved"],
                                     reply_markup=create_keyboards(list()))

            await msg.answer(languages[data["user_lang"]]["main_menu"],
                             reply_markup=create_keyboards(languages[data["user_lang"]]["btn_main_menu_for_user"],
                                                           cancel_btn=True, user_lang=data["user_lang"]))
        await state.reset_data()
        await FSMWorkProgram.main_menu.set()

    def run_handler(self):
        dp.register_message_handler(self.start_event_handler,
                                    Text(equals=languages["to_all"]["events"], ignore_case=True),
                                    state=[FSMWorkProgram.main_menu, FSMWorkProgram.admin_main_menu])
        dp.register_message_handler(self.choice_event,
                                    state=FSMWorkProgram.event_main_menu)
        dp.register_message_handler(self.reg_on_event,
                                    state=FSMWorkProgram.choice_event)
        dp.register_message_handler(self.save_reg,
                                    state=FSMWorkProgram.reg_on_event)
