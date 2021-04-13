from aiogram import types

from loader import dp, bot, _
from keyboards.reply.reply_kb import markup_profile_menu, back_kb, markup_edit_profile
from models.db_service import DBService
from states.menu_states import Menu, AboutMe


dbs = DBService()


@dp.message_handler(state=AboutMe.check_input)
async def about_me_check_input(message: types.Message):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    user_id = message.chat.id
    user = await dbs.users.get_user(user_id)

    if _("Изменить имя") in in_text:
        await AboutMe.check_input_name.set()
        markup = await back_kb()

        bot_text = _('Текущее имя пользователя: {}\nВведите новое имя в одну строку, пробелы допускаются').format(user.name)
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    elif _("Изменить обо мне") in in_text:
        await AboutMe.check_input_about.set()
        markup = await back_kb()
        if user.link:
            link = user.link
        else:
            link = 'не заданы'

        bot_text = _('Текущая ссылка и описание: {}\n\nВведите текст, 180 символов, включая ссылку, по которой могут '
                     'обращаться участники вашего круга').format(link)
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    elif _("Назад") in in_text:
        await Menu.profile_menu.set()
        markup = await markup_profile_menu()
        await bot.send_message(message.chat.id, _("Профиль"), reply_markup=markup)


@dp.message_handler(state=AboutMe.check_input_about)
async def about_me_check(message: types.Message):
    link = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    user_id = message.chat.id
    user = await dbs.users.get_user(user_id)

    if _('Назад') in link:
        await AboutMe.check_input.set()
        markup = await markup_edit_profile()
        if user.link:
            link = user.link
        else:
            link = 'не заданы'

        bot_text = _('Текущее имя пользователя: {}\n').format(user.name)
        bot_text += _('Текущая ссылка и описание: {}').format(link)
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        return

    if len(link) > 180:
        text = _("Длина текста не должна превышать 180 символов!\nПопробуйте снова.")
        await bot.send_message(message.chat.id, text)
        return

    await dbs.users.update_user(user_id, link=link)

    await Menu.profile_menu.set()
    markup = await markup_profile_menu()
    bot_text = 'Ваша новая ссылка и описание:\n{}'.format(link)
    await bot.send_message(message.chat.id, bot_text, reply_markup=markup)


@dp.message_handler(state=AboutMe.check_input_name)
async def edit_my_name_check(message: types.Message):
    user_name = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    user_id = message.chat.id
    user = await dbs.users.get_user(user_id)

    if _('Назад') in user_name:
        await AboutMe.check_input.set()
        markup = await markup_edit_profile()
        if user.link:
            link = user.link
        else:
            link = 'не заданы'

        bot_text = _('Текущее имя пользователя: {}\n').format(user.name)
        bot_text += _('Текущая ссылка и описание: {}').format(link)
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        return

    if len(user_name) > 180:
        text = _("Длина текста не должна превышать 180 символов!\nПопробуйте снова.")
        await bot.send_message(message.chat.id, text)
        return

    await dbs.users.update_user(user_id, name=user_name)

    await Menu.profile_menu.set()
    markup = await markup_profile_menu()
    bot_text = 'Ваше новое имя пользователя\n{}'.format(user_name)
    await bot.send_message(message.chat.id, bot_text, reply_markup=markup)