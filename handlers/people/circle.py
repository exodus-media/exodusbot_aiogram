from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize

from keyboards.reply.reply_kb import markup_peoples_menu, back_kb
from loader import dp, bot, _
from models.db_service import DBService
from states.menu_states import Participants, Menu
from utils.functions import get_info_text_user_for_circle, is_digit, text_sum_digit, check_number_dict, \
    get_all_info_text_user, show_help_to_me, show_help_from_me, text_input_number_people

dbs = DBService()


async def show_socium(telegram_id, state: FSMContext):
    bot_username = (await bot.me).username

    list_my_socium = await dbs.rings_help.get_my_socium(telegram_id)

    string_name = ''
    dict_socium = {}
    count = 0
    for id_help in list_my_socium:
        count += 1
        dict_socium[count] = id_help
        text_user = await get_info_text_user_for_circle(id_help, bot_username)
        string_name += f"{count}. {text_user}\n"

    await state.update_data(dict_socium=dict_socium)

    return string_name


@dp.message_handler(lambda message: emojize(_("Моя сеть :busts_in_silhouette:")) in message.text,
                    state=Menu.peoples_menu)
async def my_socium(message: types.Message, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)

    result_text = _('Все участники вашей сети:\n')

    result_text += await show_socium(message.chat.id, state)

    result_text += await text_input_number_people()

    await Participants.select_participant.set()
    markup = await back_kb()

    await bot.send_message(message.chat.id, result_text, reply_markup=markup, disable_web_page_preview=True)


async def markup_select_participant(telegram_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    user = await dbs.users.get_user(telegram_id)

    list_intentions_to = await dbs.intentions.get_intentions(statuses=[1, 11, 12, 13], to_id=telegram_id)
    set_intentions_ids_to = set([intention.from_id for intention in list_intentions_to])
    intentions_to_count = len(set_intentions_ids_to)

    list_intentions_from = await dbs.intentions.get_intentions(statuses=[1, 11, 12, 13], from_id=telegram_id)
    set_intentions_ids_from = set([intention.to_id for intention in list_intentions_from])
    intentions_from_count = len(set_intentions_ids_from)

    btn1 = emojize(_("Сеть :busts_in_silhouette: {}")).format(user.name)
    btn2 = emojize(f"{user.name} → :busts_in_silhouette: {intentions_from_count}")
    btn3 = emojize(f"{intentions_to_count} :busts_in_silhouette: → {user.name}")
    btn4 = _("Меню")

    markup.add(btn2, btn3)
    markup.add(btn1, btn4)

    return markup


@dp.message_handler(state=Participants.select_participant)
async def check_my_socium(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Назад") in in_text:
        await Menu.peoples_menu.set()
        markup = await markup_peoples_menu(message.chat.id)
        await bot.send_message(message.chat.id, _("Участники"), reply_markup=markup)
        return

    if not await is_digit(in_text):
        text = await text_sum_digit()
        await bot.send_message(message.chat.id, text)
        return

    data = await state.get_data()
    dict_socium = data["dict_socium"]

    if in_text not in dict_socium:
        text = await check_number_dict()
        await bot.send_message(message.chat.id, text)
        return

    telegram_id_from_socium = dict_socium[in_text]
    await state.update_data(telegram_id_from_socium=telegram_id_from_socium)

    bot_username = (await bot.me).username
    full_text = await get_all_info_text_user(bot_username, telegram_id_from_socium)
    await Participants.view_other_user.set()
    markup = await markup_select_participant(telegram_id_from_socium)

    await bot.send_message(message.chat.id, full_text, reply_markup=markup, disable_web_page_preview=True)


@dp.message_handler(state=Participants.select_other_participant)
async def check_other_socium(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Назад") in in_text:
        data = await state.get_data()
        telegram_id_from_socium = data["telegram_id_from_socium"]

        bot_username = (await bot.me).username
        full_text = await get_all_info_text_user(bot_username, telegram_id_from_socium)
        await Participants.view_other_user.set()
        markup = await markup_select_participant(telegram_id_from_socium)
        await bot.send_message(message.chat.id, full_text, reply_markup=markup, disable_web_page_preview=True)

        return

    if not await is_digit(in_text):
        text = await text_sum_digit()
        await bot.send_message(message.chat.id, text)
        return

    data = await state.get_data()
    dict_socium = data["dict_socium"]

    if in_text not in dict_socium:
        text = await check_number_dict()
        await bot.send_message(message.chat.id, text)
        return

    telegram_id_from_socium = dict_socium[in_text]
    await state.update_data(telegram_id_from_socium=telegram_id_from_socium)

    bot_username = (await bot.me).username
    full_text = await get_all_info_text_user(bot_username, telegram_id_from_socium)
    await Participants.view_other_user.set()
    markup = await markup_select_participant(telegram_id_from_socium)

    await bot.send_message(message.chat.id, full_text, reply_markup=markup, disable_web_page_preview=True)


@dp.message_handler(state=Participants.view_other_user)
async def view_other_user(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    data = await state.get_data()
    telegram_id_from_socium = data["telegram_id_from_socium"]

    user = await dbs.users.get_user(telegram_id_from_socium)
    text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

    if _("Сеть") in in_text:
        result_text = _('В сети участника:\n')

        result_text += await show_socium(telegram_id_from_socium, state)

        result_text += await text_input_number_people()

        await Participants.select_other_participant.set()
        markup = await back_kb()

        await bot.send_message(message.chat.id, result_text, reply_markup=markup, disable_web_page_preview=True)

        return
    elif emojize(":busts_in_silhouette: →") in in_text:

        bot_username = (await bot.me).username
        text_help_to_me = await show_help_to_me(telegram_id_from_socium, bot_username, state)

        if not text_help_to_me:
            text = _('В пользу {} нет активных транзакций').format(text_link_user)
            await bot.send_message(message.chat.id, text)
            return

        result_text = emojize(f":busts_in_silhouette: → {text_link_user}\n")
        result_text += text_help_to_me
        result_text += await text_input_number_people()

        await Participants.select_other_participant.set()
        markup = await back_kb()

        await bot.send_message(message.chat.id, result_text, reply_markup=markup, disable_web_page_preview=True)
    elif emojize("→ :busts_in_silhouette:") in in_text:

        bot_username = (await bot.me).username
        text_help_from_me = await show_help_from_me(telegram_id_from_socium, bot_username, state)
        if not text_help_from_me:
            text = _('От {} в пользу других участников нет активных транзакций').format(text_link_user)
            await bot.send_message(message.chat.id, text)
            return

        result_text = emojize(f"{text_link_user} → :busts_in_silhouette:\n")
        result_text += text_help_from_me
        result_text += await text_input_number_people()

        await Participants.select_other_participant.set()
        markup = await back_kb()

        await bot.send_message(message.chat.id, result_text, reply_markup=markup, disable_web_page_preview=True)
    elif _("Меню") in in_text:
        await Menu.peoples_menu.set()
        markup = await markup_peoples_menu(message.chat.id)
        await bot.send_message(message.chat.id, _("Участники"), reply_markup=markup)
        return






