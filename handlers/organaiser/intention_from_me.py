import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize

from loader import dp, bot, _
from keyboards.reply.reply_kb import markup_general_menu, back_kb, markup_organaiser_menu, \
    intention_settings_kb, proof_yes_no_kb, proof_obligation_kb
from models.db_service import DBService
from states.menu_states import Menu, IntentionFrom
from utils.functions import is_digit, text_sum_digit, get_status_emoji, check_number_dict, create_list_intention, \
    get_info_text_user_for_invite, text_need_obligation_to_sponsor
from utils.util_bot import send_message

dbs = DBService()


async def intention_from_me(message, state: FSMContext):
    markup = await back_kb()
    intentions = await dbs.intentions.get_intentions(statuses=[1], from_id=message.chat.id)
    obligations = await dbs.intentions.get_intentions(statuses=[11], from_id=message.chat.id)

    data = await state.get_data()
    dict_intention_from = data["dict_intention_from"]
    list_intention = await create_list_intention(dict_intention_from, from_id=True)
    text = emojize(_("Вами записано {} :heart: и {} :handshake:\n{}\n")).format(len(intentions), len(obligations),
                                                                                list_intention)
    text += _("Введите номер записи, чтобы посмотреть подробную информацию или изменить")
    await IntentionFrom.list_intention.set()
    await bot.send_message(message.chat.id, text, reply_markup=markup)


async def text_intention_from(intention_id):
    intention = await dbs.intentions.get_intention_from_id(intention_id)
    user = await dbs.users.get_user(intention.to_id)
    status = await get_status_emoji(user.status)
    text = emojize(
        _("Ваше :heart: в пользу {} {} на {} {}").format(user.name, status, intention.payment, intention.currency))
    return text


@dp.message_handler(state=IntentionFrom.list_intention)
async def dict_intention_from_menu(message: types.Message, state: FSMContext):
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
    dict_intention_from = data["dict_intention_from"]

    if in_text not in dict_intention_from:
        text = await check_number_dict()
        await bot.send_message(message.chat.id, text)
        return

    id_intention_from = dict_intention_from[in_text]
    intention = await dbs.intentions.get_intention_from_id(id_intention_from)
    if intention.status == 1:
        text_intention = await text_intention_from(id_intention_from)
        await state.update_data(id_intention_from=id_intention_from)
        markup_intention_settings_kb = await intention_settings_kb()
        await IntentionFrom.intention_settings.set()

        await bot.send_message(message.chat.id, text_intention, reply_markup=markup_intention_settings_kb)

    elif intention.status == 11:
        text_obligation = await text_need_obligation_to_sponsor(id_intention_from)
        await state.update_data(id_intention_from=id_intention_from)
        markup_obligation_settings_kb = await proof_obligation_kb()
        await IntentionFrom.obligation_settings.set()

        await bot.send_message(message.chat.id, text_obligation, reply_markup=markup_obligation_settings_kb)


async def cancel_text_intention_from(intention_id):
    intention = await dbs.intentions.get_intention_from_id(intention_id)
    user = await dbs.users.get_user(intention.to_id)
    status = await get_status_emoji(user.status)
    text = emojize(_("Вы хотите отменить свое :heart: участнику {} {} на {} {}?")).format(user.name, status,
                                                                                          intention.payment,
                                                                                          intention.currency)
    return text


async def text_change_intention(intention_id):
    intention = await dbs.intentions.get_intention_from_id(intention_id)
    text = emojize(_("Ваше :heart: было на сумму {} {}\n"
                     "Введите новую сумму (только число) в валюте {}")).format(intention.payment,
                                                                               intention.currency,
                                                                               intention.currency)
    return text


async def text_intention_to_obligation(intention_id, for_me=False, for_to=False):
    bot_username = (await bot.me).username

    intention = await dbs.intentions.get_intention_from_id(intention_id)

    if for_me:
        text = emojize(f"{intention.payment}:heart: → 🤝\n")
        text += _("кто: ") + await get_info_text_user_for_invite(intention.from_id, bot_username, for_me=True)
        text += _("\nкому: ") + await get_info_text_user_for_invite(intention.to_id, bot_username)
    elif for_to:
        text = emojize(f"{intention.payment}:heart: → 🤝\n")
        text += _("кто: ") + await get_info_text_user_for_invite(intention.from_id, bot_username)
        text += _("\nкому: ") + await get_info_text_user_for_invite(intention.to_id, bot_username, for_me=True)
    else:
        text = emojize(f"{intention.payment}:heart: → 🤝\n")
        text += _("кто: ") + await get_info_text_user_for_invite(intention.from_id, bot_username)
        text += _("\nкому: ") + await get_info_text_user_for_invite(intention.to_id, bot_username)

    return text


async def text_obligation_from_proof(obligation_id):
    obligation = await dbs.intentions.get_intention_from_id(obligation_id)
    user = await dbs.users.get_user(obligation.to_id)
    status = await get_status_emoji(user.status)
    text = emojize(_("Пожалуйста, подтвердите, что вы исполнили 🤝 на сумму "
                     "{} {} → {} {}")).format(obligation.payment, obligation.currency, user.name, status)
    return text


@dp.message_handler(state=IntentionFrom.intention_settings)
async def intention_settings_menu(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)
    data = await state.get_data()

    if _("Отменить") in in_text:
        id_intention_from = data["id_intention_from"]
        text_cancel = await cancel_text_intention_from(id_intention_from)
        markup = await proof_yes_no_kb()

        await IntentionFrom.cancel_intention.set()
        await bot.send_message(message.chat.id, text_cancel, reply_markup=markup)
        return
    elif _('Изменить') in in_text:
        id_intention_from = data["id_intention_from"]
        text = await text_change_intention(id_intention_from)
        markup = await back_kb()

        await IntentionFrom.change_intention.set()
        await bot.send_message(message.chat.id, text, reply_markup=markup)

    elif emojize(_('В :handshake:')) in in_text:
        id_intention_from = data["id_intention_from"]
        intention = await dbs.intentions.get_intention_from_id(id_intention_from)

        await dbs.intentions.update_status_from_id(id_intention_from, status=11)

        text_from = await text_intention_to_obligation(id_intention_from, for_me=True)

        # отправляем тому, кто просил помощь
        text_to = await text_intention_to_obligation(id_intention_from, for_to=True)
        await bot.send_message(intention.to_id, text_to, disable_web_page_preview=True)

        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, text_from, reply_markup=markup, disable_web_page_preview=True)

        # отправляем тому, кто участвует в помощи
        text_for_circle_invite = await text_intention_to_obligation(id_intention_from)
        list_circle_invite = await dbs.rings_help.get_my_socium_small(intention.to_id)
        list_circle_invite.discard(intention.from_id)
        for tg_id in list_circle_invite:
            await send_message(tg_id, text_for_circle_invite, disable_web_page_preview=True)
            await asyncio.sleep(.05)

        return
    elif _('Назад') in in_text:
        await intention_from_me(message, state)
        return
    elif _('Исполнить') in in_text:
        id_intention_from = data["id_intention_from"]
        text = await text_obligation_from_proof(id_intention_from)

        markup = await proof_yes_no_kb()
        await IntentionFrom.obligation_send_proof.set()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
        return
    elif _('Меню') in in_text:
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, _('Меню'), reply_markup=markup)


async def send_messages_other_change_intention(id_intention_from):
    bot_username = (await bot.me).username

    intention = await dbs.intentions.get_intention_from_id(id_intention_from)

    to_id = intention.to_id
    from_id = intention.from_id

    # текст для получателя помощи
    text_for_to_id = emojize(_("Изменение :heart:\n"))
    text_for_to_id += _("кто: ") + await get_info_text_user_for_invite(intention.from_id, bot_username)
    text_for_to_id += _("\nкому: ") + await get_info_text_user_for_invite(intention.to_id, bot_username, for_me=True)
    await bot.send_message(to_id, text_for_to_id, disable_web_page_preview=True)

    # текст для всех причастных к помощи
    text_for_circle_invite = emojize(_("Изменение :heart:\n"))
    text_for_circle_invite += _("кто: ") + await get_info_text_user_for_invite(intention.from_id, bot_username)
    text_for_circle_invite += _("\nкому: ") + await get_info_text_user_for_invite(intention.to_id, bot_username)

    list_circle_invite = await dbs.rings_help.get_my_socium_small(to_id)
    list_circle_invite.discard(from_id)

    for tg_id in list_circle_invite:
        await send_message(tg_id, text_for_circle_invite, disable_web_page_preview=True)
        await asyncio.sleep(.05)


@dp.message_handler(state=IntentionFrom.change_intention)
async def change_intention_menu(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    data = await state.get_data()
    id_intention_from = data["id_intention_from"]

    if _('Назад') in in_text:
        text_intention = await text_intention_from(id_intention_from)
        markup_intention_settings_kb = await intention_settings_kb()
        await IntentionFrom.intention_settings.set()
        await bot.send_message(message.chat.id, text_intention, reply_markup=markup_intention_settings_kb)
        return

    if not await is_digit(in_text):
        text = await text_sum_digit()
        await bot.send_message(message.chat.id, text)
        return

    await dbs.intentions.update_payment_from_id(id_intention_from, payment=in_text)

    text_intention = await text_intention_from(id_intention_from)
    markup_intention_settings_kb = await intention_settings_kb()
    await IntentionFrom.intention_settings.set()
    await bot.send_message(message.chat.id, text_intention, reply_markup=markup_intention_settings_kb)

    # отправляем всем причастным
    await send_messages_other_change_intention(id_intention_from)

    return


async def cancel_intention(state: FSMContext):
    data = await state.get_data()
    id_intention_from = data["id_intention_from"]

    intention = await dbs.intentions.get_intention_from_id(id_intention_from)

    user_to = await dbs.users.get_user(intention.to_id)
    user_from = await dbs.users.get_user(intention.from_id)

    text_to = emojize(_("{} отменил своё :heart: в вашу пользу на сумму {} {}")).format(user_from.name,
                                                                                        intention.payment,
                                                                                        intention.currency)
    text_from = emojize(_("Ваше :heart: участнику {} на {} {} отменено.")).format(user_to.name, intention.payment,
                                                                                  intention.currency)

    await dbs.intentions.update_status_from_id(id_intention_from, status=0)
    await dbs.rings_help.delete_from_help_array(intention.to_id, intention.from_id)

    await Menu.global_menu.set()
    markup = await markup_general_menu()
    await bot.send_message(intention.to_id, text_to, reply_markup=markup)
    await bot.send_message(intention.from_id, text_from, reply_markup=markup)

    # отправляем тому, кто участвует в помощи
    text_for_circle_invite = emojize(_("{} отменил своё :heart: участнику {} на {} {}.")).format(user_from.name,
                                                                                                 user_to.name,
                                                                                                 intention.payment,
                                                                                                 intention.currency)
    list_circle_invite = await dbs.rings_help.get_my_socium_small(intention.to_id)
    list_circle_invite.discard(intention.from_id)
    for tg_id in list_circle_invite:
        await send_message(tg_id, text_for_circle_invite)
        await asyncio.sleep(.05)


@dp.message_handler(state=IntentionFrom.cancel_intention)
async def cancel_intention_menu(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Да") in in_text:
        await cancel_intention(state)
        return
    elif _("Нет") in in_text:
        data = await state.get_data()
        id_intention_from = data["id_intention_from"]
        text_intention = await text_intention_from(id_intention_from)
        markup_intention_settings_kb = await intention_settings_kb()
        await IntentionFrom.intention_settings.set()
        await bot.send_message(message.chat.id, text_intention, reply_markup=markup_intention_settings_kb)

        return


@dp.message_handler(state=IntentionFrom.obligation_settings)
async def obligation_settings_menu(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Да") in in_text:
        data = await state.get_data()
        id_obligation_from = data["id_intention_from"]
        text = await text_obligation_from_proof(id_obligation_from)

        markup = await proof_yes_no_kb()
        await IntentionFrom.obligation_send_proof.set()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
        return

    elif _("Назад") in in_text:
        await intention_from_me(message, state)
        return


async def text_obligation_final(obligation_id):
    bot_username = (await bot.me).username

    obligation = await dbs.intentions.get_intention_from_id(obligation_id)

    text = emojize(f"{obligation.payment}🤝 → 👍\n")
    text += _("кто: ") + await get_info_text_user_for_invite(obligation.from_id, bot_username, for_me=True)
    text += _("\nкому: ") + await get_info_text_user_for_invite(obligation.to_id, bot_username)

    return text


async def text_obligation_final_for_need_user(obligation_id):
    bot_username = (await bot.me).username

    obligation = await dbs.intentions.get_intention_from_id(obligation_id)

    text = emojize(f"{obligation.payment}🤝 → 👍\n")
    text += _("кто: ") + await get_info_text_user_for_invite(obligation.from_id, bot_username)
    text += _("\nкому: ") + await get_info_text_user_for_invite(obligation.to_id, bot_username, for_me=True)

    return text


async def text_obligation_final_for_circle(obligation_id):
    bot_username = (await bot.me).username

    obligation = await dbs.intentions.get_intention_from_id(obligation_id)

    text = emojize(f"{obligation.payment}🤝 → 👍\n")
    text += _("кто: ") + await get_info_text_user_for_invite(obligation.from_id, bot_username)
    text += _("\nкому: ") + await get_info_text_user_for_invite(obligation.to_id, bot_username)

    return text


@dp.message_handler(state=IntentionFrom.obligation_send_proof)
async def obligation_send_final(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Да") in in_text:
        data = await state.get_data()
        id_obligation_from = data["id_intention_from"]

        await dbs.intentions.update_status_from_id(id_obligation_from, status=12)

        obligation = await dbs.intentions.get_intention_from_id(id_obligation_from)

        text_from = await text_obligation_final(id_obligation_from)
        text_to = await text_obligation_final_for_need_user(id_obligation_from)

        await Menu.organaiser_menu.set()
        markup = await markup_organaiser_menu()

        await bot.send_message(obligation.to_id, text_to, disable_web_page_preview=True)
        await bot.send_message(message.chat.id, text_from, reply_markup=markup, disable_web_page_preview=True)

        # отправляем тому, кто участвует в помощи
        text_for_circle_invite = await text_obligation_final_for_circle(id_obligation_from)
        list_circle_invite = await dbs.rings_help.get_my_socium_small(obligation.to_id)
        list_circle_invite.discard(obligation.from_id)
        for tg_id in list_circle_invite:
            await send_message(tg_id, text_for_circle_invite, disable_web_page_preview=True)
            await asyncio.sleep(.05)

        return

    elif _("Нет") in in_text:
        await intention_from_me(message, state)
        return
