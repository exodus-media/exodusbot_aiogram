from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize

from keyboards.reply.reply_kb import markup_general_menu, back_kb, markup_peoples_menu
from loader import dp, bot, _
from models.db_service import DBService
from states.menu_states import Participants, Menu
from utils.functions import get_info_text_user_for_circle, show_help_to_me, show_help_from_me, text_input_number_people

dbs = DBService()


async def expand_my_socium(telegram_id):
    list_my_socium = await dbs.rings_help.get_my_socium(telegram_id)

    list_expand_socium = []

    # пробегаем мою сеть
    for id_my in list_my_socium:
        # для каждого из моей сети строим его сеть
        other_socium = await dbs.rings_help.get_my_socium(id_my)
        # пробегаем его сеть
        for id_other in other_socium:
            # если очередного юзера нет в моей сети
            if id_other not in list_my_socium:
                user = await dbs.users.get_user(id_other)
                # если этому юзеру нужна помощь(оранжевый), то дабвляем в расширенный список сети
                if user.status == "orange":
                    list_expand_socium.append(id_other)

    list_expand_socium = set(list_expand_socium)
    list_expand_socium.discard(telegram_id)

    if len(list_expand_socium) == 0:
        meta_txt = _("Нет новых участников")
        await bot.send_message(telegram_id, meta_txt)
        return
    else:
        string_name = ''
        dict_my_expand = {}
        count = 0
        bot_username = (await bot.me).username

        for id_help in list_expand_socium:
            count += 1
            dict_my_expand[count] = id_help
            text_user = await get_info_text_user_for_circle(id_help, bot_username)
            string_name += f"{count}. {text_user}\n"

        bot_text = _('Расширение сети:{}').format(string_name)

        await bot.send_message(telegram_id, bot_text, disable_web_page_preview=True)


@dp.message_handler(lambda message: emojize(":busts_in_silhouette: → :bust_in_silhouette:") in message.text,
                    state=Menu.peoples_menu)
async def record_for_me(message: types.Message, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)

    bot_username = (await bot.me).username
    text_help_to_me = await show_help_to_me(message.chat.id, bot_username, state)

    if not text_help_to_me:
        text = _('Нет участников, которые помогали вам')
        await bot.send_message(message.chat.id, text)
        return

    tg_user = await dbs.users.get_user(message.chat.id)
    result_text = emojize(f":busts_in_silhouette: → {tg_user.name}\n")
    result_text += text_help_to_me
    result_text += await text_input_number_people()

    await Participants.select_participant.set()
    markup = await back_kb()

    await bot.send_message(message.chat.id, result_text, reply_markup=markup, disable_web_page_preview=True)


@dp.message_handler(lambda message: emojize(":bust_in_silhouette: → ") in message.text,
                    state=Menu.peoples_menu)
async def record_from_me(message: types.Message, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)

    bot_username = (await bot.me).username
    text_help_from_me = await show_help_from_me(message.chat.id, bot_username, state)
    if not text_help_from_me:
        text = _('Нет участников, которым вы помогали')
        await bot.send_message(message.chat.id, text)
        return

    tg_user = await dbs.users.get_user(message.chat.id)
    result_text = emojize(f"{tg_user.name} → :busts_in_silhouette:\n")
    result_text += text_help_from_me
    result_text += await text_input_number_people()

    await Participants.select_participant.set()
    markup = await back_kb()

    await bot.send_message(message.chat.id, result_text, reply_markup=markup, disable_web_page_preview=True)


@dp.message_handler(lambda message: _("Расширить сеть") in message.text,
                    state=Menu.peoples_menu)
async def expand_socium(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)
    await expand_my_socium(message.chat.id)
    return


async def show_help_socium(telegram_id):
    bot_username = (await bot.me).username

    list_my_socium = await dbs.rings_help.get_my_socium(telegram_id)

    # добавляем себя, чтобы в списке можно было б свою ссылку взять
    list_my_socium.add(telegram_id)

    string_name = ''
    count = 0
    for id_help in list_my_socium:
        user_help = await dbs.users.get_user(id_help)
        if user_help.status == "green":
            continue

        intentions = await dbs.intentions.get_intentions(from_id=telegram_id, to_id=id_help, statuses=[1, 11, 12])
        if intentions:
            continue

        count += 1
        text_user = await get_info_text_user_for_circle(id_help, bot_username)
        string_name += f"{count}. {text_user}\n"

    return string_name


@dp.message_handler(lambda message: emojize(_(":link: Помочь")) in message.text,
                    state=Menu.peoples_menu)
async def get_help_menu(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)

    text_help_socium = await show_help_socium(message.chat.id)

    if text_help_socium:
        text = _('В вашей сети нуждаются в помощи:\n\n')
        text += text_help_socium

        await Participants.to_help.set()
        markup = await back_kb()
        await bot.send_message(message.chat.id, text, reply_markup=markup, disable_web_page_preview=True)
        return
    else:
        text = _("В вашей сети нет нуждающихся в помощи")
        await bot.send_message(message.chat.id, text)
        return


@dp.message_handler(state=Participants.to_help)
async def check_my_socium(message: types.Message):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Назад") in in_text:
        await Menu.peoples_menu.set()
        markup = await markup_peoples_menu(message.chat.id)
        await bot.send_message(message.chat.id, _("Участники"), reply_markup=markup)
        return


@dp.message_handler(lambda message: _("Меню") in message.text,
                    state=Menu.peoples_menu)
async def to_main_menu(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)
    await Menu.global_menu.set()
    markup = await markup_general_menu()
    await bot.send_message(message.chat.id, _('Меню'), reply_markup=markup)
