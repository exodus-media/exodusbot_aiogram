from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize

from keyboards.reply.reply_kb import markup_general_menu, back_kb, markup_peoples_menu
from loader import dp, bot, _
from models.db_service import DBService
from states.menu_states import Participants, Menu
from utils.functions import get_info_text_user_for_circle, show_help_to_me, show_help_from_me

dbs = DBService()