from aiogram import types
from initial import bot, dp
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from initial import DataClient
from keyboards import create_keyboards
from config import FSMWorkProgram


class LandmarkSettings:
    btn_landmark_settings = ["Добавить город",
                             "Добавить дост-ть",
                             "Добавить факт"]
    btn_admin_main_menu = ["Виртуальный Гид",
                           "Викторины",
                           "О проекте",
                           "Системные настройки"]

    def __init__(self, data_client: DataClient):
        self.data_client = data_client

    def check_town_title(self, town_title: str) -> [bool, str]:
        if town_title:
            if not self.data_client.town_exist(town_title):
                return [True, f"Сохранить следующий город: {town_title}?"]
            else:
                return [False, "Такое название уже добавлено."]
        else:
            return [False, "Неккоректное название.\nПовторите"]

    def check_landmark_title(self, landmark_title: str, town_id: int) -> [bool, str]:
        if landmark_title:
            if not self.data_client.landmark_exist(landmark_title=landmark_title, town_id=town_id):
                return [True, f"Эта достопримечательность будет добавлена"]
            else:
                return [False, "Такая достопримечательность уже добавлена для этого города."]
        else:
            return [False, "Неккоректное название.\nПовторите"]

    def check_fact_title(self, fact_title: str, landmark_id: int, town_id: int) -> [bool, str]:
        if fact_title:
            if not self.data_client.fact_exist(fact_title=fact_title, landmark_id=landmark_id, town_id=town_id):
                return [True, f"Этот факт будет добавлен"]
            else:
                return [False, "Такой факт уже добавлен для этой дост-ти."]
        else:
            return [False, "Неккоректное название.\nПовторите"]

    async def start_landmark_settings(self, msg: types.Message):
        await msg.answer("Выберите, что хотите изменить",
                         reply_markup=create_keyboards(self.btn_landmark_settings))
        await FSMWorkProgram.landmark_settings.set()

    @staticmethod
    async def start_set_new_town(msg: types.Message):
        await msg.answer("Введите название нового города.",
                         reply_markup=create_keyboards(list(), cancel_btn=True))
        await FSMWorkProgram.set_new_town.set()

    async def set_new_town(self, msg: types.Message, state: FSMContext):
        result = self.check_town_title(msg.text)
        if result[0]:
            async with state.proxy() as data:
                data["town_title"] = msg.text
            await msg.answer(result[1],
                             reply_markup=create_keyboards(list(), yes_no_btn=True))
            await FSMWorkProgram.save_new_town.set()
        else:
            await msg.answer(result[1])

    async def save_new_town(self, msg: types.Message, state: FSMContext):
        if msg.text == "Да":
            async with state.proxy() as data:
                result = self.data_client.set_new_town(data["town_title"])
            await msg.answer("Название города добавлено.",
                             reply_markup=create_keyboards(self.btn_admin_main_menu))
            await FSMWorkProgram.admin_main_menu.set()
            await state.proxy().clear()
        else:
            await msg.answer("Введите другое название.",
                             reply_markup=create_keyboards(list(), cancel_btn=True))
            await FSMWorkProgram.set_new_town.set()
            await state.proxy().clear()

    async def start_set_new_landmark(self, msg: types.Message):
        back_msg = "Веберите город, для которого хотите добавить достопримечательность."
        town_btn = self.data_client.get_all_town_title()
        await msg.answer(back_msg,
                         reply_markup=create_keyboards(town_btn, cancel_btn=True))
        await FSMWorkProgram.set_new_landmark.set()

    async def set_town_id_landmark(self, msg: types.Message, state: FSMContext):
        if self.data_client.town_exist(msg.text):
            town_id = self.data_client.get_town_id(town_title=msg.text)
            async with state.proxy() as data:
                data["town_title"] = msg.text
                data["town_id"] = town_id
            await msg.answer("Введите название достопримечательности",
                             reply_markup=create_keyboards(list(), cancel_btn=True))
            await FSMWorkProgram.set_town_id_landmark.set()
        else:
            await msg.answer("Неккоректное название. Выберите город из предложенных.")

    async def set_title_landmark(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            result = self.check_landmark_title(landmark_title=msg.text, town_id=data["town_id"])
            if result[0]:
                data["landmark_title"] = msg.text
                await msg.answer("Введите ссылку на изображение достопримечательности.",
                                 reply_markup=create_keyboards(list(), cancel_btn=True))
                await FSMWorkProgram.set_title_landmark.set()
            else:
                await msg.answer(result[1])

    @staticmethod
    async def set_image_link_landmark(msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["image_link"] = msg.text
            back_msg = f"Сохранить достопримечательность?" \
                       f"{data['landmark_title']}\n" \
                       f"В городе: {data['town_title']}\n" \
                       f"Ссылка на картинку: {data['image_link']}"
            await msg.answer(back_msg,
                             reply_markup=create_keyboards(list(), yes_no_btn=True))
        await FSMWorkProgram.set_image_link_landmark.set()

    async def save_new_landmark(self, msg: types.Message, state: FSMContext):
        if msg.text == "Да":
            async with state.proxy() as data:
                result = self.data_client.set_new_landmark(town_id=data["town_id"],
                                                           title=data["landmark_title"],
                                                           image_link=data["image_link"])
            await msg.answer("Достопримечательность добавлена.",
                             reply_markup=create_keyboards(self.btn_admin_main_menu))
            await FSMWorkProgram.admin_main_menu.set()
            await state.proxy().clear()
        else:
            town_btn = self.data_client.get_all_town_title()
            await msg.answer("Начнем с начала. Веберите город.",
                             reply_markup=create_keyboards(town_btn, cancel_btn=True))
            await FSMWorkProgram.set_new_landmark.set()
            await state.proxy().clear()

        await FSMWorkProgram.save_new_landmark.set()

    async def start_set_new_fact(self, msg: types.Message, state: FSMContext):
        back_msg = "Веберите город, для которого хотите добавить достопримечательность."
        town_btn = self.data_client.get_all_town_title()
        await msg.answer(back_msg,
                         reply_markup=create_keyboards(town_btn, cancel_btn=True))
        await FSMWorkProgram.set_new_fact.set()

    async def set_town_id_fact(self, msg: types.Message, state: FSMContext):
        if self.data_client.town_exist(msg.text):
            town_id = self.data_client.get_town_id(town_title=msg.text)
            async with state.proxy() as data:
                data["town_title"] = msg.text
                data["town_id"] = town_id
            landmark_btn = self.data_client.get_all_landmark_by_town_id(town_id=town_id)
            await msg.answer("Введите название дост-ти, которой посвящен факт",
                             reply_markup=create_keyboards(landmark_btn, cancel_btn=True))
            await FSMWorkProgram.set_town_id_fact.set()
        else:
            await msg.answer("Неккоректное название. Выберите город из предложенных.")

    async def set_landmark_id_fact(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if self.data_client.landmark_exist(town_id=data["town_id"], landmark_title=msg.text):
                landmark_id = self.data_client.get_landmark_id(town_id=data["town_id"],
                                                               landmark_title=msg.text)
                data["landmark_title"] = msg.text
                data["landmark_id"] = landmark_id
                await msg.answer("Введите название для нового факта.",
                                 reply_markup=create_keyboards(list(), cancel_btn=True))
                await FSMWorkProgram.set_landmark_id_fact.set()
            else:
                await msg.answer("Неккоректное название. Выберите дост-сть из предложенных.")

    async def set_title_fact(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            result = self.check_fact_title(fact_title=msg.text, town_id=data["town_id"], landmark_id=data["landmark_id"])
            if result[0]:
                data["fact_title"] = msg.text
                await msg.answer("Введите текст нового факта.",
                                 reply_markup=create_keyboards(list(), cancel_btn=True))
                await FSMWorkProgram.set_title_fact.set()
            else:
                await msg.answer(result[1])

    @staticmethod
    async def set_text_fact(msg: types.Message, state: FSMContext):
        if len(msg.text) > 10:
            async with state.proxy() as data:
                data["fact_text"] = msg.text
            await msg.answer("Введите ссылку на аудиоматериал, если такая есть.",
                             reply_markup=create_keyboards(["Без аудио"], cancel_btn=True))
            await FSMWorkProgram.set_text_fact.set()
        else:
            await msg.answer("Неккоректно написано.")

    @staticmethod
    async def set_audio_fact(msg: types.Message, state: FSMContext):
        if msg.text != "Без аудио":
            await msg.answer("Ссылка принята.")
        else:
            await msg.answer("Хорошо, этот факт будет без аудиозаписи.")
        async with state.proxy() as data:
            data["audio_link"] = msg.text
        await msg.answer("Теперь введите ссылку на картинку, если такая есть.",
                         reply_markup=create_keyboards(["Без картинки"], cancel_btn=True))
        await FSMWorkProgram.set_audio_fact.set()

    @staticmethod
    async def set_image_link_fact(msg: types.Message, state: FSMContext):
        if msg.text != "Без картинки":
            await msg.answer("Ссылка принята.")
        else:
            await msg.answer("Хорошо, этот факт будет без картинки.")
        async with state.proxy() as data:
            data["image_link"] = msg.text
        back_msg = f"Сохранить новый факт?\nГород: {data['town_title']}\nДост-ть: {data['landmark_title']}\n" \
                   f"Название факта: {data['fact_title']}\nТекст факта: {data['fact_text']}\n" \
                   f"Ссылка на аудиозапись: {data['audio_link']}\nСсылка на картинку: {msg.text}"
        await msg.answer(back_msg,
                         reply_markup=create_keyboards(list(), yes_no_btn=True))

        await FSMWorkProgram.set_image_link_fact.set()

    async def save_new_fact(self, msg: types.Message, state: FSMContext):
        if msg.text == "Да":
            async with state.proxy() as data:
                result = self.data_client.set_new_fact(landmark_id=data["landmark_id"],
                                                       title=data["fact_title"],
                                                       text=data["fact_text"],
                                                       audio=data["audio_link"],
                                                       image_link=data["image_link"])
            await msg.answer("Новый факт добавлен.",
                             reply_markup=create_keyboards(self.btn_admin_main_menu))
            await FSMWorkProgram.admin_main_menu.set()
            await state.proxy().clear()
        else:
            town_btn = self.data_client.get_all_town_title()
            await msg.answer("Начнем с начала. Выберите город.",
                             reply_markup=create_keyboards(town_btn, cancel_btn=True))
            await FSMWorkProgram.set_new_fact.set()
            await state.proxy().clear()

    def run_handler(self):
        dp.register_message_handler(self.start_landmark_settings,
                                    Text(equals="Достопримечательности", ignore_case=True),
                                    state=FSMWorkProgram.admin_settings)

        dp.register_message_handler(self.start_set_new_town,
                                    Text(equals="Добавить город", ignore_case=True),
                                    state=FSMWorkProgram.landmark_settings)
        dp.register_message_handler(self.set_new_town,
                                    state=FSMWorkProgram.set_new_town)
        dp.register_message_handler(self.save_new_town,
                                    state=FSMWorkProgram.save_new_town)

        dp.register_message_handler(self.start_set_new_landmark,
                                    Text(equals="Добавить дост-ть", ignore_case=True),
                                    state=FSMWorkProgram.landmark_settings)
        dp.register_message_handler(self.set_town_id_landmark,
                                    state=FSMWorkProgram.set_new_landmark)
        dp.register_message_handler(self.set_title_landmark,
                                    state=FSMWorkProgram.set_town_id_landmark)
        dp.register_message_handler(self.set_image_link_landmark,
                                    state=FSMWorkProgram.set_title_landmark)
        dp.register_message_handler(self.save_new_landmark,
                                    state=FSMWorkProgram.set_image_link_landmark)

        dp.register_message_handler(self.start_set_new_fact,
                                    Text(equals="Добавить факт", ignore_case=True),
                                    state=FSMWorkProgram.landmark_settings)
        dp.register_message_handler(self.set_town_id_fact,
                                    state=FSMWorkProgram.set_new_fact)
        dp.register_message_handler(self.set_landmark_id_fact,
                                    state=FSMWorkProgram.set_town_id_fact)
        dp.register_message_handler(self.set_title_fact,
                                    state=FSMWorkProgram.set_landmark_id_fact)
        dp.register_message_handler(self.set_text_fact,
                                    state=FSMWorkProgram.set_title_fact)
        dp.register_message_handler(self.set_audio_fact,
                                    state=FSMWorkProgram.set_text_fact)
        dp.register_message_handler(self.set_image_link_fact,
                                    state=FSMWorkProgram.set_audio_fact)
        dp.register_message_handler(self.save_new_fact,
                                    state=FSMWorkProgram.set_image_link_fact)
