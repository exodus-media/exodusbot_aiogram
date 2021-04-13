from aiogram import types
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from aiogram.utils.emoji import emojize

from models.db_service import DBService

dbc = DBService()


inline_btn_1 = InlineKeyboardButton('Первая кнопка!', callback_data='button1')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)

# Отдадим пользователю клавиатуру с выбором языков
languages_markup = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="English", callback_data="lang_en")
        ]
    ]
)


async def change_status_inline_kb():
    user_from_tg = types.User.get_current()
    user_from_db = await dbc.users.get_user(user_from_tg.id)
    status = user_from_db.status

    if 'green' in status:
        status_markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(text=emojize(":sos:"), callback_data="red_status"),
                    InlineKeyboardButton(text=emojize(":high_brightness:"), callback_data="orange_status"),
                    InlineKeyboardButton(text="Назад", callback_data="back")
                ]
            ]
        )
    if "orange" in status:
        status_markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(text=emojize(":sos:"), callback_data="red_status"),
                    InlineKeyboardButton(text=emojize(":white_check_mark:"), callback_data="orange_status"),
                    InlineKeyboardButton(text="Назад", callback_data="back")
                ]
            ]
        )
    if "red" in status:
        status_markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(text=emojize(":high_brightness:"), callback_data="red_status"),
                    InlineKeyboardButton(text=emojize(":white_check_mark:"), callback_data="orange_status"),
                    InlineKeyboardButton(text="Назад", callback_data="back")
                ]
            ]
        )

    return status_markup