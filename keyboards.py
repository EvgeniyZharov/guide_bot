from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from languages.languages import languages


def create_keyboards(btn_list: list, cancel_btn: bool = False, control_btn: bool = False,
                     back_btn: bool = False, yes_no_btn: bool = False, user_lang: str = "ru"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for elem in btn_list:
        kb.add(KeyboardButton(elem))
    if control_btn:
        kb.add(KeyboardButton(">"))
        kb.add(KeyboardButton("<"))
    if yes_no_btn:
        kb.add(KeyboardButton(languages[user_lang]["yes_btn"]))
        kb.add(KeyboardButton(languages[user_lang]["no_btn"]))
    if cancel_btn:
        kb.add(KeyboardButton(languages[user_lang]["cancel_btn"]))
    if back_btn:
        kb.add(KeyboardButton(languages[user_lang]["back_btn"]))

    return kb


