from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize

from loader import dp, bot, _
from keyboards.reply.reply_kb import markup_general_menu, back_kb, markup_organaiser_menu, proof_yes_no_kb, \
    check_intention_for_me, check_obligation_for_me
from models.db_service import DBService
from states.menu_states import Menu, IntentionTo
from utils.functions import is_digit, text_sum_digit, get_status_emoji, check_number_dict, create_list_intention, \
    text_intention_to, text_need_intention_to_obligation, text_need_intention_to_sponsor, text_obligation_to, \
    text_need_obligation, text_need_obligation_to_sponsor, text_proof_forgive_obligation_from, \
    text_final_forgive_obligation_from, text_forgive_obligation_to

dbs = DBService()


async def global_menu(message):
    await Menu.global_menu.set()
    markup = await markup_general_menu()
    await bot.send_message(message.chat.id, _('Меню'), reply_markup=markup)


async def intention_to_me(message, state: FSMContext):
    markup = await back_kb()
    intentions = await dbs.intentions.get_intentions(statuses=[1], to_id=message.chat.id)
    obligations = await dbs.intentions.get_intentions(statuses=[11], to_id=message.chat.id)

    data = await state.get_data()
    dict_intention_to = data["dict_intention_to"]
    list_intention = await create_list_intention(dict_intention_to, to_id=True)
    text = emojize(_("В вашу пользу {} :heart: и {} :handshake:\n{}\n")).format(len(intentions), len(obligations),
                                                                                list_intention)
    text += _("Введите номер записи, чтобы посмотреть подробную информацию или изменить")
    await IntentionTo.list_intention.set()
    await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(state=IntentionTo.list_intention)
async def dict_intention_to_menu(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Назад") in in_text:
        await Menu.organaiser_menu.set()
        markup = await markup_organaiser_menu()
        user = await dbs.users.get_user(message.chat.id)
        emoji_status = await get_status_emoji(user.status)
        text = _("Органайзер") + emoji_status
        await bot.send_message(message.chat.id, text, reply_markup=markup)
        return

    if not await is_digit(in_text):
        text = await text_sum_digit()
        await bot.send_message(message.chat.id, text)
        return

    data = await state.get_data()
    dict_intention_to = data["dict_intention_to"]

    if in_text not in dict_intention_to:
        text = await check_number_dict()
        await bot.send_message(message.chat.id, text)
        return

    id_intention_to = dict_intention_to[in_text]
    intention = await dbs.intentions.get_intention_from_id(id_intention_to)
    if intention.status == 1:
        text_intention = await text_intention_to(id_intention_to)
        await state.update_data(id_intention_to=id_intention_to)
        markup_intention_settings_kb = await check_intention_for_me()
        await IntentionTo.intention_settings.set()

        await bot.send_message(message.chat.id, text_intention, reply_markup=markup_intention_settings_kb)

    elif intention.status == 11:
        text_obligation = await text_obligation_to(id_intention_to)
        await state.update_data(id_obligation_to=id_intention_to)
        markup_obligation_settings_kb = await check_obligation_for_me()
        await IntentionTo.obligation_settings.set()

        await bot.send_message(message.chat.id, text_obligation, reply_markup=markup_obligation_settings_kb)


@dp.message_handler(state=IntentionTo.intention_settings)
async def intention_to_me_settings_menu(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Попросить") in in_text:
        data = await state.get_data()
        id_intention_to = data["id_intention_to"]
        intention = await dbs.intentions.get_intention_from_id(id_intention_to)

        text_me = await text_need_intention_to_obligation()
        await bot.send_message(message.chat.id, text_me)

        text_to = await text_need_intention_to_sponsor(id_intention_to)
        await bot.send_message(intention.from_id, text_to)

        await intention_to_me(message, state)
        return
    elif _("Назад") in in_text:
        await intention_to_me(message, state)
        return
    elif _("Меню") in in_text:
        await global_menu(message)
        return


@dp.message_handler(state=IntentionTo.obligation_settings)
async def obligation_to_me_settings_menu(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)
    data = await state.get_data()
    id_obligation_to = data["id_obligation_to"]
    obligation = await dbs.intentions.get_intention_from_id(id_obligation_to)

    if _("Запрос") in in_text:
        text_me = await text_need_obligation(id_obligation_to)
        await bot.send_message(message.chat.id, text_me)

        text_to = await text_need_obligation_to_sponsor(id_obligation_to)
        await bot.send_message(obligation.from_id, text_to)

        await intention_to_me(message, state)
        return
    elif _("Простить") in in_text:
        text_me = await text_proof_forgive_obligation_from(id_obligation_to)
        await IntentionTo.obligation_forgive_proof.set()
        markup = await proof_yes_no_kb()
        await bot.send_message(message.chat.id, text_me, reply_markup=markup)
        return

    elif _("Назад") in in_text:
        await intention_to_me(message, state)
        return
    elif _("Меню") in in_text:
        await global_menu(message)
        return


@dp.message_handler(state=IntentionTo.obligation_forgive_proof)
async def obligation_to_me_forgive(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)
    data = await state.get_data()
    id_obligation_to = data["id_obligation_to"]
    obligation = await dbs.intentions.get_intention_from_id(id_obligation_to)

    if _("Да") in in_text:
        text_from = await text_final_forgive_obligation_from(id_obligation_to)
        text_to = await text_forgive_obligation_to(id_obligation_to)

        await dbs.intentions.update_status_from_id(id_obligation_to, status=0, active=0)

        await bot.send_message(message.chat.id, text_from)
        await bot.send_message(obligation.from_id, text_to)

        await global_menu(message)
        return
    elif _("Нет") in in_text:
        text_obligation = await text_obligation_to(id_obligation_to)

        markup_obligation_settings_kb = await check_obligation_for_me()
        await IntentionTo.obligation_settings.set()

        await bot.send_message(message.chat.id, text_obligation, reply_markup=markup_obligation_settings_kb)
        return