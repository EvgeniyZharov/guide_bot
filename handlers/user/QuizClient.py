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


class QuizClient:
    # quiz_menu_btn = ["Статистика", "Играть"]

    def __init__(self, data_client: DataClient):
        self.data_client = data_client

    def delete_space(self, elem_list: list):
        new_elem_list = list()
        for elem in elem_list:
            if elem != "space":
                new_elem_list.append(elem)
        return new_elem_list

    async def user_quiz_menu(self, msg: types.Message):
        user_lang = self.data_client.get_user_lang(user_id=str(msg.from_user.id))
        await msg.answer(languages[user_lang]["user_quiz_menu"],
                         reply_markup=create_keyboards(languages[user_lang]["quiz_menu_btn"], cancel_btn=True,
                                                       user_lang=user_lang))
        await FSMWorkProgram.user_quiz_menu.set()

    async def get_statistic(self, msg: types.Message):
        user_lang = self.data_client.get_user_lang(user_id=str(msg.from_user.id))
        user_id = self.data_client.get_user_id(msg.from_user.id)
        data = self.data_client.get_statistics(user_id=user_id, user_lang=user_lang)
        await msg.answer(data)

    async def get_quiz_theme(self, msg: types.Message):
        user_lang = self.data_client.get_user_lang(user_id=str(msg.from_user.id))

        result = self.data_client.get_quiz_theme_list(user_lang=user_lang)
        if result[0]:
            btn = result[1]
            await msg.answer(languages[user_lang]["get_quiz_theme"],
                             reply_markup=create_keyboards(btn, cancel_btn=True,
                                                           user_lang=user_lang))
            await FSMWorkProgram.get_quiz_theme.set()
        else:
            await msg.answer(languages[user_lang]["get_quiz_theme_not"])

    async def get_quiz(self, msg: types.Message, state: FSMContext):
        user_lang = self.data_client.get_user_lang(user_id=str(msg.from_user.id))
        quiz_theme_id = self.data_client.get_quiz_theme_id(msg.text)
        async with state.proxy() as data:
            data["quiz_theme_id"] = quiz_theme_id
            data["quiz_theme_title"] = msg.text
        btn = self.data_client.get_quiz_list(quiz_theme_id)[1]
        await msg.answer(languages[user_lang]["get_quiz"],
                         reply_markup=create_keyboards(btn, cancel_btn=True,
                                                       user_lang=user_lang))
        await FSMWorkProgram.get_quiz.set()

    async def run_quiz(self, msg: types.Message, state: FSMContext):
        user_lang = self.data_client.get_user_lang(user_id=str(msg.from_user.id))
        async with state.proxy() as data:
            quiz_id = self.data_client.get_quiz_id(msg.text)
            if not self.data_client.user_quiz_exist(user_id=msg.from_user.id, quiz_id=quiz_id):
                data["quiz_id"] = quiz_id
                data["quiz_title"] = msg.text
                quiz_ask = self.data_client.get_random_ask(quiz_id=data["quiz_id"], ask_id_ready=list())
                ask = quiz_ask["ask"]
                answers = [quiz_ask["t_q"], quiz_ask["f_q1"], quiz_ask["f_q2"], quiz_ask["f_q3"]]
                answers = self.delete_space(answers)
                shuffle(answers)
                image_id = quiz_ask["image_id"]
                data["true_q"] = quiz_ask["t_q"]
                data["big_answer"] = quiz_ask["big_answer"]
                data["ask_id"] = [quiz_ask["id"]]
                data["user_id"] = self.data_client.get_user_id(msg.from_user.id)
                await msg.answer_photo(image_id, ask,
                                       reply_markup=create_keyboards(answers, cancel_btn=True,
                                                                     user_lang=user_lang))
                await FSMWorkProgram.run_quiz.set()
            else:
                await msg.answer(languages[user_lang]["run_quiz_already_finished"])

    async def quiz(self, msg: types.Message, state: FSMContext):
        user_lang = self.data_client.get_user_lang(user_id=str(msg.from_user.id))
        async with state.proxy() as data:
            if data["true_q"] == msg.text:
                back_msg = languages[user_lang]["true_answer"]
                if data["big_answer"] != "no":
                    back_msg += f"\n\n{data['big_answer']}" if data['big_answer'] != "space" else ""
                await msg.answer(back_msg)
                score = 10
            else:
                back_msg = languages[user_lang]["error_answer"] + f"{data['true_q']}."
                if data["big_answer"] != "no":
                    back_msg += f"\n\n{data['big_answer']}" if data['big_answer'] != "space" else ""
                await msg.answer(back_msg)
                score = 0
            self.data_client.set_score_user_quiz(user_id=data["user_id"], quiz_id=data["quiz_id"], score=score)
            quiz_ask = self.data_client.get_random_ask(quiz_id=data["quiz_id"], ask_id_ready=data["ask_id"])
            if len(data["ask_id"]) < 5:
                ask = quiz_ask["ask"]
                answers = [quiz_ask["t_q"], quiz_ask["f_q1"], quiz_ask["f_q2"], quiz_ask["f_q3"]]
                answers = self.delete_space(answers)
                shuffle(answers)
                image_id = quiz_ask["image_id"]
                data["true_q"] = quiz_ask["t_q"]
                data["big_answer"] = quiz_ask["big_answer"]
                data["ask_id"].append(quiz_ask["id"])
                # print(data["ask_id"])
                await msg.answer_photo(image_id, ask,
                                       reply_markup=create_keyboards(answers, cancel_btn=True,
                                                                     user_lang=user_lang))
            else:
                await msg.answer(languages[user_lang]["quiz_all_ask"],
                                 reply_markup=create_keyboards(list(), cancel_btn=True,
                                                               user_lang=user_lang))

    def run_handler(self) -> None:
        dp.register_message_handler(self.user_quiz_menu,
                                    Text(equals=languages["to_all"]["quizzes"], ignore_case=True),
                                    state=FSMWorkProgram.main_menu)

        dp.register_message_handler(self.get_statistic,
                                    Text(equals=languages["to_all"]["statistic"], ignore_case=True),
                                    state=FSMWorkProgram.user_quiz_menu)

        dp.register_message_handler(self.get_quiz_theme,
                                    Text(equals=languages["to_all"]["play"], ignore_case=True),
                                    state=FSMWorkProgram.user_quiz_menu)
        dp.register_message_handler(self.get_quiz,
                                    state=FSMWorkProgram.get_quiz_theme)
        dp.register_message_handler(self.run_quiz,
                                    state=FSMWorkProgram.get_quiz)
        dp.register_message_handler(self.quiz,
                                    state=FSMWorkProgram.run_quiz)




