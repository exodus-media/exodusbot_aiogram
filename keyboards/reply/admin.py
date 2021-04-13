from aiogram import types
from aiogram.utils.emoji import emojize

from data.config import ADMIN
from loader import _
from utils.functions import get_status_emoji, get_intentions_count_sum_to, get_intentions_count_sum_from, \
    get_all_obligations_count_sum_to, get_all_obligations_count_sum_from


async def markup_admin_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    btn1 = _("Список пользователей")
    btn2 = _("Отправить уведомление")
    btn3 = _("Меню")

    markup.add(btn1, btn2, btn3)
    return markup


async def markup_send_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    btn1 = _("Да")
    btn2 = _("Нет")
    btn3 = _("Меню")

    markup.add(btn1, btn2, btn3)
    return markup

