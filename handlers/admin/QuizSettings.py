from aiogram import types
from initial import bot, dp
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from initial import DataClient

from keyboards import create_keyboards
from config import FSMWorkProgram


class QuizSettings:
    btn_quiz_settings = ["Добавить тему",
                         "Добавить квиз",
                         "Добавить вопрос"]
    btn_admin_main_menu = ["Виртуальный Гид",
                           "Викторины",
                           "О проекте",
                           "Системные настройки"]

    def __init__(self, data_client: DataClient):
        self.data_client = data_client

    async def start_quiz_settings(self, msg: types.Message):
        await msg.answer("Выберите, что хотите изменить",
                         reply_markup=create_keyboards(self.btn_quiz_settings))
        await FSMWorkProgram.quiz_settings.set()

    @staticmethod
    async def set_new_quiz_theme(msg: types.Message):
        await msg.answer("Введите название новой темы для квиза.",
                         reply_markup=create_keyboards(list(), cancel_btn=True))
        await FSMWorkProgram.set_new_quiz_theme.set()

    async def set_quiz_theme_title(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["title"] = msg.text
        await msg.answer("Введите описание для новой темы квиза.")
        await FSMWorkProgram.set_quiz_theme_title.set()

    async def set_quiz_theme_description(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["description"] = msg.text
            back_msg = f"Сохранить следующие данные про новую тему?\n" \
                       f"Название: {data['title']}\nОписание: {data['description']}."
        await msg.answer(back_msg,
                         reply_markup=create_keyboards(list(), yes_no_btn=True, cancel_btn=True))
        await FSMWorkProgram.set_quiz_theme_description.set()

    async def save_new_quiz_theme(self, msg: types.Message, state: FSMContext):
        if msg.text == "Да":
            async with state.proxy() as data:
                result = self.data_client.set_new_quiz_theme(title=data["title"],
                                                             description=data["description"])
            await msg.answer("Данные сохранены.",
                             reply_markup=create_keyboards(self.btn_quiz_settings, cancel_btn=True))
            await FSMWorkProgram.quiz_settings.set()
        else:
            await msg.answer("Давайте начнем сначала, введите название темы.",
                             reply_markup=create_keyboards(list(), cancel_btn=True))
            await FSMWorkProgram.set_new_quiz_theme.set()

    async def set_new_quiz(self, msg: types.Message):
        btn = self.data_client.get_quiz_theme_list()[1]
        print(btn)
        await msg.answer("Выберите для какой темы хотите создать новый квиз.",
                         reply_markup=create_keyboards(btn, cancel_btn=True))
        await FSMWorkProgram.set_new_quiz.set()

    async def set_quiz_group_id(self, msg: types.Message, state: FSMContext):
        if msg.text:
            theme_id = self.data_client.get_quiz_theme_id(msg.text)
            async with state.proxy() as data:
                data["theme_title"] = msg.text
                data["theme_id"] = theme_id
            await msg.answer("Введите название для нового квиза.",
                             reply_markup=create_keyboards(list(), cancel_btn=True))
            await FSMWorkProgram.set_quiz_group_id.set()

    async def set_quiz_title(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["quiz_title"] = msg.text
        await msg.answer("Введите описание для нового квиза.")
        await FSMWorkProgram.set_quiz_title.set()

    async def set_quiz_description(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["quiz_description"] = msg.text
            back_msg = f"Сохранить следующие данные про новую тему?\n" \
                       f"Тема квиза: {data['theme_title']}\n" \
                       f"Название: {data['quiz_title']}\nОписание: {data['quiz_description']}."
        await msg.answer(back_msg,
                         reply_markup=create_keyboards(list(), yes_no_btn=True, cancel_btn=True))
        await FSMWorkProgram.set_quiz_description.set()

    async def save_new_quiz(self, msg: types.Message, state: FSMContext):
        if msg.text == "Да":
            async with state.proxy() as data:
                result = self.data_client.set_new_quiz(theme_id=data["theme_id"],
                                                       title=data["quiz_title"],
                                                       description=data["quiz_description"])
            await msg.answer("Данные сохранены.",
                             reply_markup=create_keyboards(self.btn_quiz_settings, cancel_btn=True))
            await FSMWorkProgram.quiz_settings.set()
        else:
            btn = self.data_client.get_quiz_theme_list()[1]
            await msg.answer("Давайте начнем сначала, выберите тему для квиза.",
                             reply_markup=create_keyboards(btn, cancel_btn=True))
            await FSMWorkProgram.set_new_quiz.set()

    async def set_new_quiz_ask(self, msg: types.Message):
        btn = self.data_client.get_quiz_theme_list()[1]
        await msg.answer("Выберите для какой темы хотите создать новый вопрос.",
                         reply_markup=create_keyboards(btn, cancel_btn=True))
        await FSMWorkProgram.set_new_quiz_ask.set()

    async def set_quiz_theme_id_ask(self, msg: types.Message, state: FSMContext):
        if msg.text:
            theme_id = self.data_client.get_quiz_theme_id(msg.text)
            async with state.proxy() as data:
                data["theme_title"] = msg.text
                data["theme_id"] = theme_id
            btn = self.data_client.get_quiz_list(theme_id=theme_id)[1]
            await msg.answer("Выберите название квиза, для которого хотите добавить вопрос.",
                             reply_markup=create_keyboards(btn, cancel_btn=True))
            await FSMWorkProgram.set_quiz_theme_id_ask.set()

    async def set_quiz_id_ask(self, msg: types.Message, state: FSMContext):
        if msg.text:
            quiz_id = self.data_client.get_quiz_id(msg.text)
            async with state.proxy() as data:
                data["quiz_title"] = msg.text
                data["quiz_id"] = quiz_id
            # btn = self.data_client.get_quiz_list(theme_id=theme_id)[1]
            await msg.answer("Введите вопрос.",
                             reply_markup=create_keyboards(list(), cancel_btn=True))
            await FSMWorkProgram.set_quiz_id_ask.set()

    async def set_quiz_ask(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["quiz_ask"] = msg.text
        await msg.answer("Введите ответы на вопрос (в формате: t/f/f/f).")
        await FSMWorkProgram.set_quiz_ask.set()

    async def set_questions(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["quiz_questions"] = msg.text
        await msg.answer("Отправивьте картинку, если планируется.")
        await FSMWorkProgram.set_questions.set()

    async def set_quiz_ask_image(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["image_id"] = msg.photo[-1]["file_id"]
            data["quiz_description"] = msg.text
            back_msg = f"Сохранить следующие данные по вопросу?\n" \
                       f"Тема квиза: {data['theme_title']}\n" \
                       f"Квиз: {data['quiz_title']}\n" \
                       f"Вопрос: {data['quiz_ask']}\nОтветы: {data['quiz_questions']}\n" \
                       f"Ссылка на фото: {data['image_id']}."
        await msg.answer_photo(data["image_id"], back_msg,
                               reply_markup=create_keyboards(list(), yes_no_btn=True, cancel_btn=True))
        await FSMWorkProgram.set_quiz_ask_image.set()

    async def save_new_quiz_ask(self, msg: types.Message, state: FSMContext):
        if msg.text == "Да":
            async with state.proxy() as data:
                quests = data["quiz_questions"].split("/")
                result = self.data_client.set_new_quiz_ask(quiz_id=data["quiz_id"],
                                                           quiz_ask=data["quiz_ask"],
                                                           t_q=quests[0],
                                                           f_q1=quests[1],
                                                           f_q2=quests[2],
                                                           f_q3=quests[3],
                                                           image_id=data["image_id"])
            await msg.answer("Данные сохранены. Введите новый вопрос.",
                             reply_markup=create_keyboards(list(), cancel_btn=True))
            await FSMWorkProgram.set_quiz_id_ask.set()
        else:
            await msg.answer("Информация не сохранена. Введите новый вопрос.",
                             reply_markup=create_keyboards(list(), cancel_btn=True))
            await FSMWorkProgram.set_quiz_id_ask.set()

    def run_handler(self):
        dp.register_message_handler(self.start_quiz_settings,
                                    Text(equals="Квиз", ignore_case=True),
                                    state=FSMWorkProgram.admin_settings)

        dp.register_message_handler(self.set_new_quiz_theme,
                                    Text(equals="Добавить тему", ignore_case=True),
                                    state=FSMWorkProgram.quiz_settings)
        dp.register_message_handler(self.set_quiz_theme_title,
                                    state=FSMWorkProgram.set_new_quiz_theme)
        dp.register_message_handler(self.set_quiz_theme_description,
                                    state=FSMWorkProgram.set_quiz_theme_title)
        dp.register_message_handler(self.save_new_quiz_theme,
                                    state=FSMWorkProgram.set_quiz_theme_description)

        dp.register_message_handler(self.set_new_quiz,
                                    Text(equals="Добавить квиз", ignore_case=True),
                                    state=FSMWorkProgram.quiz_settings)
        dp.register_message_handler(self.set_quiz_group_id,
                                    state=FSMWorkProgram.set_new_quiz)
        dp.register_message_handler(self.set_quiz_title,
                                    state=FSMWorkProgram.set_quiz_group_id)
        dp.register_message_handler(self.set_quiz_description,
                                    state=FSMWorkProgram.set_quiz_title)
        dp.register_message_handler(self.save_new_quiz,
                                    state=FSMWorkProgram.set_quiz_description)

        dp.register_message_handler(self.set_new_quiz_ask,
                                    Text(equals="Добавить вопрос", ignore_case=True),
                                    state=FSMWorkProgram.quiz_settings)
        dp.register_message_handler(self.set_quiz_theme_id_ask,
                                    state=FSMWorkProgram.set_new_quiz_ask)
        dp.register_message_handler(self.set_quiz_id_ask,
                                    state=FSMWorkProgram.set_quiz_theme_id_ask)
        dp.register_message_handler(self.set_quiz_ask,
                                    state=FSMWorkProgram.set_quiz_id_ask)
        dp.register_message_handler(self.set_questions,
                                    state=FSMWorkProgram.set_quiz_ask)
        dp.register_message_handler(self.set_quiz_ask_image,
                                    content_types=['photo'],
                                    state=FSMWorkProgram.set_questions)
        dp.register_message_handler(self.save_new_quiz_ask,
                                    state=FSMWorkProgram.set_quiz_ask_image)

