import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, bot, _
from models.db_service import DBService

from keyboards.reply.reply_kb import markup_organaiser_menu, markup_peoples_menu, \
    markup_faq_menu, markup_profile_menu, markup_general_menu
from keyboards.reply.admin import markup_admin_menu, markup_send_menu

from states.menu_states import Menu, Admin
from utils.functions import get_all_info_text_user, get_status_emoji, get_short_info_text_user, text_faq
from utils.util_bot import send_message

dbs = DBService()


async def global_menu(message):
    await Menu.global_menu.set()
    markup = await markup_general_menu()
    await bot.send_message(message.chat.id, _('Меню'), reply_markup=markup)


async def admin_view(message):
    await Admin.main_menu.set()

    markup = await markup_admin_menu()

    users = await dbs.users.get_all_users()
    text = _("Количество пользователей бота: {}").format(len(users))

    await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(lambda message: _("Органайзер") in message.text, state=Menu.global_menu)
async def organaiser_handler(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)

    await Menu.organaiser_menu.set()
    markup = await markup_organaiser_menu()
    user = await dbs.users.get_user(message.chat.id)
    emoji_status = await get_status_emoji(user.status)
    text = _("Органайзер") + emoji_status
    await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(lambda message: _("Профиль") in message.text, state=Menu.global_menu)
async def profile_handler(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)

    await Menu.profile_menu.set()
    markup = await markup_profile_menu()
    bot_username = (await bot.me).username

    text = await get_all_info_text_user(bot_username, message.chat.id)

    await bot.send_message(message.chat.id, text, reply_markup=markup, disable_web_page_preview=True)


@dp.message_handler(lambda message: _("Участники") in message.text, state=Menu.global_menu)
async def peoples_handler(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)

    await Menu.peoples_menu.set()
    markup = await markup_peoples_menu(message.chat.id)
    await bot.send_message(message.chat.id, _("Участники"), reply_markup=markup)


@dp.message_handler(lambda message: "FAQ" in message.text, state=Menu.global_menu)
async def faq_handler(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)

    await Menu.faq_menu.set()

    markup = await markup_faq_menu()
    text = await text_faq()
    await bot.send_message(message.chat.id, text, reply_markup=markup, disable_web_page_preview=True)


@dp.message_handler(lambda message: _("Администратор") in message.text, state=Menu.global_menu)
async def admin_handler(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)

    await admin_view(message)


@dp.message_handler(state=Admin.main_menu)
async def admin_main_menu(message: types.Message):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Список") in in_text:
        list_all_users = await dbs.users.get_all_users()

        string_name = ''
        for count, user in enumerate(list_all_users):
            text_user = await get_short_info_text_user(user.tg_id)
            string_name += f"{count+1}. {text_user}"

        await bot.send_message(message.chat.id, string_name)
        return
    elif _("Отправить") in in_text:
        text = _("Введите текст для отправки пользователям")
        markup = types.ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
        await Admin.send_menu.set()
        return
    elif _("Меню") in in_text:
        await global_menu(message)
        return


@dp.message_handler(state=Admin.send_menu)
async def admin_send_menu(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    text = _("Вы ввели текст для отправки")
    await bot.send_message(message.chat.id, text)
    await bot.send_message(message.chat.id, in_text)

    markup = await markup_send_menu()
    await Admin.check_send_menu.set()
    await state.update_data(admin_text=in_text)

    await bot.send_message(message.chat.id, _('Подтвердите отправку'), reply_markup=markup)


@dp.message_handler(state=Admin.check_send_menu)
async def admin_check_send_menu(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _('Да') in in_text:
        list_user_for_message = await dbs.users.get_all_users()
        data_state = await state.get_data()
        text_for_mes = data_state['admin_text']

        for user in list_user_for_message:
            await send_message(user.tg_id, text_for_mes)
            await asyncio.sleep(.05)

        await bot.send_message(message.chat.id, "Успешно отправлено")
        await admin_view(message)
        return
    elif _('Нет') in in_text:
        await bot.send_message(message.chat.id, _("Отправка отменена"))
        await admin_view(message)
        return
    elif _('Меню') in in_text:
        await global_menu(message)
        return