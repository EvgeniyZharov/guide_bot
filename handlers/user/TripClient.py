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
from config import FSMWorkProgram, BASE_IMAGE_ID

# from handlers.user.choice_place_base import ChoicePlaceBase


class TripClient:
    # quiz_menu_btn = ["Статистика", "Играть"]

    def __init__(self, data_client: DataClient):
        self.data_client = data_client

    async def start_trip_handler(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            user_lang = self.data_client.get_user_lang(user_id=str(msg.from_user.id))
            data["user_lang"] = user_lang
            # Выберите мероприятие
            btn = self.data_client.get_trip_btn(town_id=1, language=user_lang)
            await msg.answer(languages[user_lang]["start_trip"],
                             reply_markup=create_keyboards(btn, cancel_btn=True,
                                                           user_lang=user_lang))
            await FSMWorkProgram.trip_main_manu.set()

    async def choice_trip(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            trip_id = self.data_client.get_trip_id(title=msg.text)
            trip_data = self.data_client.get_trip_info(trip_id=trip_id, language=data["user_lang"])
            data["trip_title"] = msg.text
            data["trip_id"] = trip_id
            data["count_stages"] = trip_data["count_stages"]
            data["num_stage"] = 1
            # Запустить мероприятие
            btn = self.data_client.get_trip_stage_btn(trip_id=trip_id, language=data["user_lang"])
            await msg.answer(languages[data["user_lang"]]["choice_trip"],
                             reply_markup=create_keyboards(btn, cancel_btn=True,
                                                           user_lang=data["user_lang"]))
            await FSMWorkProgram.choice_trip.set()

    async def launch_trip(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            trip_stage_id = self.data_client.get_trip_stage_id(title=msg.text, trip_id=data["trip_id"],
                                                               num=data["num_stage"], language=data["user_lang"])
            trip_stage_info = self.data_client.get_trip_stage_info(trip_stage_id=trip_stage_id,
                                                                   num=data["num_stage"], language=data["user_lang"])
            text = f"{trip_stage_info['title']}\n{trip_stage_info['description']}"
            await msg.answer(text=text)
            data["trip_stage_title"] = msg.text
            data["trip_stage_id"] = trip_stage_id
            data["count_trip_elem"] = trip_stage_info["count_elem"]
            data["trip_elem_num"] = 1
            trip_elem_info = self.data_client.get_stage_element_info(trip_stage_id=trip_stage_id,
                                                                     num_elem=data["trip_elem_num"],
                                                                     language=data["user_lang"])
            # Для перехода нажми на стрелку
            text = f"{trip_elem_info['title']}\n{trip_elem_info['description']}"
            await bot.send_message(msg.from_user.id, text=languages[data["user_lang"]]["launch_trip"],
                                   reply_markup=create_keyboards(list(),
                                                                 cancel_btn=True,
                                                                 control_btn=True,
                                                                 user_lang=data["user_lang"]))

            await bot.send_photo(msg.from_user.id, photo=f"{trip_elem_info['image_link']}", caption=text)
            await bot.send_audio(msg.from_user.id, audio=f"{trip_elem_info['audio_link']}")
        await FSMWorkProgram.trip_run.set()

    async def run_trip(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if msg.text == ">":
                if data["trip_elem_num"] != data["count_trip_elem"]:
                    data["trip_elem_num"] += 1
                else:
                    await msg.answer("Это последняя страница")
                    return
            elif msg.text == "<":
                if data["trip_elem_num"] != 1:
                    data["trip_elem_num"] -= 1
                else:
                    await msg.answer("Это первая страница")
                    return
            else:
                await msg.answer("Такой функции нет")
                return
            trip_elem_info = self.data_client.get_stage_element_info(trip_stage_id=data["trip_stage_id"],
                                                                     num_elem=data["trip_elem_num"],
                                                                     language=data["user_lang"])
            text = f"{trip_elem_info['title']}\n{trip_elem_info['description']}"
            if trip_elem_info["image_link"] != "0":
                image_link = trip_elem_info["image_link"]
            else:
                image_link = BASE_IMAGE_ID
            await bot.send_photo(msg.from_user.id, photo=image_link, caption=text)
            if trip_elem_info["audio_link"] != "0":
                await bot.send_audio(msg.from_user.id, audio=f"{trip_elem_info['audio_link']}")

    async def close_run_trip(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            # Уверены, что хотите закончить экскурсию?
            await msg.answer(languages[data["user_lang"]]["close_trip"],
                             reply_markup=create_keyboards(list(), yes_no_btn=True,
                                                           user_lang=data["user_lang"]))
            await FSMWorkProgram.close_trip.set()

    async def end_run_trip(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if msg.text in languages["to_all"]["yes"]:
                await msg.answer(languages[data["user_lang"]]["close_run"],
                                 reply_markup=create_keyboards(languages[data["user_lang"]]["btn_main_menu_for_user"],
                                                               cancel_btn=True, user_lang=data["user_lang"]))
                await state.reset_data()
                await FSMWorkProgram.main_menu.set()
            elif msg.text in languages["to_all"]["no"]:
                # result = self.data_client.set_new_participant()
                await msg.answer(languages[data["user_lang"]]["continue_run"],
                                 reply_markup=create_keyboards(languages[data["user_lang"]]["trip_control"],
                                                               cancel_btn=True,
                                                               user_lang=data["user_lang"]))

    def run_handler(self):
        dp.register_message_handler(self.start_trip_handler,
                                    Text(equals=languages["to_all"]["trips"], ignore_case=True),
                                    state=[FSMWorkProgram.main_menu, FSMWorkProgram.admin_main_menu])
        dp.register_message_handler(self.choice_trip,
                                    state=FSMWorkProgram.trip_main_manu)
        dp.register_message_handler(self.launch_trip,
                                    state=FSMWorkProgram.choice_trip)
        dp.register_message_handler(self.close_run_trip,
                                    Text(equals=languages["to_all"]["close_trip"]),
                                    state=FSMWorkProgram.trip_run)
        dp.register_message_handler(self.run_trip,
                                    state=FSMWorkProgram.trip_run)
        dp.register_message_handler(self.end_run_trip,
                                    state=FSMWorkProgram.close_trip)
