from aiogram import types
from initial import bot, dp
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from initial import DataClient
from initial import languages

from keyboards import create_keyboards
from config import FSMWorkProgram
from handlers import admin_client

from handlers.user import QuizClient, RegOnEventClient, TripClient


# category_id = data_client.get_one_from_one_if("place_category", "id", "title", "Club")


class UserClient:

    # btn_main_menu_for_user = [  # "Виртуальный Гид",
    #                           "Викторины",
    #                           "Изменить язык сервиса"
    #                           # "Достопримечательности",
    #                           # "О проекте",
    #                           # "Настройки"
    # ]

    def __init__(self, data_client: DataClient):
        self.data_client = data_client
        self.AdminClient = admin_client.AdminClient(data_client=data_client)
        self.QuizClient = QuizClient.QuizClient(data_client=data_client)
        self.TripClient = TripClient.TripClient(data_client=data_client)
        self.RegOnEventClient = RegOnEventClient.RegOnEventClient(data_client=data_client)
        # self.ChoiceAnnounceProgram = ChoiceAnnounceProgram(data_client)
        # self.FindNearPlaceProgram = FindNearPlaceProgram(data_client)
        # self.FindPlaceProgram = FindPlaceProgram(data_client)
        # # Base program for FindNear, FindPlace, WatchPlaces
        # self.BaseChoicePlaceProgram = BaseChoicePlace(data_client)

    def check_user_exist(self, msg: types.Message):
        user = msg.from_user
        if not self.data_client.user_exist(user.id):
            return self.data_client.set_new_user(name=user.full_name, user_id=str(user.id))

    async def go_to_main_menu(self, msg: types.Message):
        result = self.check_user_exist(msg=msg)
        user_lang = self.data_client.get_user_lang(user_id=str(msg.from_user.id))
        back_msg = languages[user_lang]["main_menu"]
        await msg.reply(back_msg,
                        reply_markup=create_keyboards(languages[user_lang]["btn_main_menu_for_user"]))
        await FSMWorkProgram.main_menu.set()

    async def test_db(self, msg: types.Message):
        back_msg = self.data_client.get_all_data()
        await msg.reply(back_msg)

    async def test_user_db(self, msg: types.Message):
        back_msg = self.data_client.get_user_data()
        await msg.reply(back_msg)

    async def test_user_quiz_db(self, msg: types.Message):
        back_msg = self.data_client.get_user_quiz_data()
        await msg.reply(back_msg)

    # async def test_func(self, msg: types.Message):
    #     back_msg = "testing"
    #     await msg.answer(back_msg,
    #                      reply_markup=create_keyboards(list(), yes_no_btn=True))

    async def test_audio(self, msg: types.Message):
        await msg.answer(msg.audio.file_id)
        await msg.answer_audio(msg.audio.file_id, "Testing")

    async def get_image_id(self, msg: types.Message):
        await msg.answer(msg.photo[-1]["file_id"])

    async def get_audio_id(self, msg: types.Message):
        await msg.answer(msg.audio.file_id)

    async def start_work(self, msg: types.Message):
        result = self.check_user_exist(msg=msg)
        user_lang = self.data_client.get_user_lang(user_id=str(msg.from_user.id))
        back_msg = languages[user_lang]["menu_after_start"]
        await msg.reply(back_msg,
                        reply_markup=create_keyboards(languages[user_lang]["btn_main_menu_for_user"]))
        await FSMWorkProgram.main_menu.set()
        # print(self.data_client.get_all_reserves())

    async def change_user_lang(self, msg: types.Message):
        result = self.check_user_exist(msg=msg)
        user_lang = self.data_client.get_user_lang(user_id=str(msg.from_user.id))
        if user_lang == "ru":
            new_lang = "en"
        else:
            new_lang = "ru"
        result_2 = self.data_client.change_user_lang(user_id=str(msg.from_user.id), new_lang=new_lang)
        if result_2:
            await msg.answer(languages[new_lang]["change_lang_true"],
                             reply_markup=create_keyboards(languages[new_lang]["btn_main_menu_for_user"]))
        else:
            await msg.answer("error")

    async def set_new_admin(self, msg: types.Message):
        result = self.data_client.set_new_admin(str(msg.from_user.id))
        if result:
            await msg.reply("Вам доступны функции администратора.",
                            reply_markup=create_keyboards(["Перейти"]))
            await FSMWorkProgram.to_admin_main_menu.set()

    async def about_project(self, msg: types.Message):
        user_lang = self.data_client.get_user_lang(user_id=str(msg.from_user.id))
        back_msg = languages[user_lang]["about_project_info"]
        await msg.answer(back_msg)

    async def get_manual(self, msg: types.Message):
        user_lang = self.data_client.get_user_lang(user_id=str(msg.from_user.id))
        back_msg = languages[user_lang]["manual_info"]
        await msg.answer(back_msg)

    @staticmethod
    async def about_us(msg: types.Message):
        back_msg = "Проект: Виртуальный гид"
        await msg.reply(back_msg)

    async def photo_id(self, msg: types.Message):
        await msg.answer_photo(msg.text)

    def run_handler(self):
        dp.register_message_handler(self.start_work, commands=["start"], state="*")
        dp.register_message_handler(self.test_db, commands=["test_db"], state="*")
        dp.register_message_handler(self.test_user_db, commands=["test_user_db"], state="*")
        dp.register_message_handler(self.test_user_quiz_db, commands=["test_user_quiz_db"], state="*")
        # dp.register_message_handler(self.test_func, commands=["test_func"], state="*")
        dp.register_message_handler(self.go_to_main_menu,
                                    Text(equals=languages["to_all"]["cancel"], ignore_case=True),
                                    state="*")
        dp.register_message_handler(self.change_user_lang,
                                    Text(equals=languages["to_all"]["change_lang"], ignore_case=True),
                                    state=[FSMWorkProgram.main_menu, FSMWorkProgram.admin_main_menu])
        dp.register_message_handler(self.about_project,
                                    Text(equals=languages["to_all"]["about_project"], ignore_case=True),
                                    state=[FSMWorkProgram.main_menu, FSMWorkProgram.admin_main_menu])
        dp.register_message_handler(self.get_manual,
                                    Text(equals=languages["to_all"]["manual"], ignore_case=True),
                                    state="*")
        dp.register_message_handler(self.set_new_admin,
                                    Text(equals="qq", ignore_case=True),
                                    state=FSMWorkProgram.main_menu)

        dp.register_message_handler(self.get_image_id,
                                    content_types=["photo"],
                                    state=FSMWorkProgram.main_menu)
        dp.register_message_handler(self.get_audio_id,
                                    content_types=["audio"],
                                    state=FSMWorkProgram.main_menu)
        # dp.register_message_handler(self.photo_id,
        #                             content_types=["text"],
        #                             state=FSMWorkProgram.main_menu)



        # Run programs for bot function

        self.QuizClient.run_handler()
        self.TripClient.run_handler()
        self.RegOnEventClient.run_handler()
        # self.FindNearPlaceProgram.run_handler()
        # self.FindPlaceProgram.run_handler()
        # self.ChoiceAnnounceProgram.run_handler()
        # # Base program for FindNear, FindPlace, WatchPlaces
        # self.BaseChoicePlaceProgram.run_handler()

        # Run function for admins
        self.AdminClient.run_handler()
