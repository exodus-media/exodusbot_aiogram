import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize

from loader import dp, bot, _
from keyboards.reply.reply_kb import back_kb, markup_organaiser_menu
from models.db_service import DBService
from states.menu_states import Menu, ProofObligation
from utils.functions import get_status_emoji, is_digit, text_sum_digit, check_number_dict, \
    get_info_text_user_for_invite, get_all_info_text_user, send_notify_for_auto_end_red
from utils.util_bot import send_message

dbs = DBService()


async def list_obligation_check_kb():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    btn1 = _('Да, я получил')
    btn2 = _('Назад')
    markup.row(btn1, btn2)

    return markup


@dp.message_handler(state=ProofObligation.list_obligation)
async def list_obligation_check(message: types.Message, state: FSMContext):
    in_text = message.text
    user_id = message.chat.id
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Назад") in in_text:
        await Menu.organaiser_menu.set()
        markup = await markup_organaiser_menu()
        user = await dbs.users.get_user(user_id)
        emoji_status = await get_status_emoji(user.status)
        text = _("Органайзер") + emoji_status
        await bot.send_message(message.chat.id, text, reply_markup=markup)
        return

    if not await is_digit(in_text):
        text = await text_sum_digit()
        await bot.send_message(message.chat.id, text)
        return

    data = await state.get_data()
    dict_obligation_proof = data["dict_obligation_proof"]

    if in_text not in dict_obligation_proof:
        text = await check_number_dict()
        await bot.send_message(message.chat.id, text)
        return

    id_obligation = dict_obligation_proof[in_text]
    await state.update_data(id_obligation_peoof=id_obligation)
    obligation = await dbs.intentions.get_intention_from_id(id_obligation)

    if obligation.from_id == user_id:
        user_to = await dbs.users.get_user(obligation.to_id)
        user_from = await dbs.users.get_user(obligation.from_id)
        status_to = await get_status_emoji(user_to.status)
        status_from = await get_status_emoji(user_from.status)

        text_to = emojize(_("{} {} исполнил в вашу пользу {} :handshake:."
                     "Пожалуйста, проверьте и подтвердите :handshake: → 👍")).format(user_from.name, status_from, obligation.payment)
        text_from = emojize(_("{} {} отправлено повторное уведомление об исполненном :handshake:")).format(user_to.name, status_to)
        await send_message(obligation.to_id, text_to)
        markup = await back_kb()

        await bot.send_message(obligation.from_id, text_from, reply_markup=markup)
        return

    elif obligation.to_id == user_id:
        user_from = await dbs.users.get_user(obligation.from_id)
        status_from = await get_status_emoji(user_from.status)

        text_from = emojize(_("{} {} -> 🤝 на сумму {}\n"
                              "Пожалуйста, проверьте ваши реквизиты и подтвердите получение:")).format(user_from.name,
                                                                                                       status_from,
                                                                                                       obligation.payment)

        markup = await list_obligation_check_kb()
        await ProofObligation.list_obligation_check.set()
        await bot.send_message(message.chat.id, text_from, reply_markup=markup)


async def send_notify_all_user(user_id, text, status):
    user = await dbs.users.get_user(user_id)
    bot_username = (await bot.me).username
    emoji_status = await get_status_emoji(status)
    text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

    text_for_other_people = f"{text_link_user} {text} {emoji_status}\n\n"
    text_for_other_people += await get_all_info_text_user(bot_username, user_id)

    my_socium = await dbs.rings_help.get_my_socium(user_id)
    for tg_id in my_socium:
        await send_message(tg_id, text_for_other_people, disable_web_page_preview=True)
        await asyncio.sleep(.05)


async def auto_return_from_red(message, obligation, user_to):
    obligations_to = await dbs.intentions.get_intentions(statuses=[13], to_id=obligation.to_id,
                                                         user_status="red")
    obligations_to_sum = 0
    for obligation in obligations_to:
        obligations_to_sum += obligation.payment

    user_from_statuses = await dbs.statuses.get_status(user_to.tg_id, type='red')
    payment = user_from_statuses.payment
    payment_to = (payment - obligations_to_sum) if payment > obligations_to_sum else 0
    if payment_to == 0:
        if user_to.status == "redorange":
            await dbs.users.update_user(message.chat.id, status="orange")

            await dbs.intentions.update_intention_status_with_tg_id(old_status=11, new_status=110,
                                                                    to_id=message.chat.id, user_status='red')
            await dbs.intentions.update_intention_status_with_tg_id(old_status=12, new_status=120,
                                                                    to_id=message.chat.id, user_status='red')
            await dbs.intentions.update_intention_status_with_tg_id(old_status=13, new_status=0,
                                                                    to_id=message.chat.id, user_status='red')

            await dbs.intentions.update_active(to_id=message.chat.id, user_status="orange", active=1)
            #await dbs.intentions.update_active(to_id=message.chat.id, user_status="red", active=0)

            await send_notify_all_user(message.chat.id, _("возвращается к"), "orange")

            text = emojize(_("Вы вернулись к :high_brightness:"))

        elif user_to.status == "redgreen":
            await dbs.users.update_user(message.chat.id, status="green")

            await dbs.intentions.update_intention_status_with_tg_id(old_status=1, new_status=0,
                                                                    to_id=message.chat.id, user_status='red')
            await dbs.intentions.update_intention_status_with_tg_id(old_status=11, new_status=110,
                                                                    to_id=message.chat.id, user_status='red')
            await dbs.intentions.update_intention_status_with_tg_id(old_status=12, new_status=120,
                                                                    to_id=message.chat.id, user_status='red')
            await dbs.intentions.update_intention_status_with_tg_id(old_status=13, new_status=0,
                                                                    to_id=message.chat.id, user_status='red')

            #await dbs.intentions.update_active(to_id=message.chat.id, user_status="red", active=0)

            await send_notify_all_user(message.chat.id, _("возвращается к"), "green")

            text = emojize(_("Вы вернулись к :white_check_mark:"))

        await bot.send_message(message.chat.id, text)

        # отправляем тому, кто участвует в помощи
        text_for_other_people = await send_notify_for_auto_end_red(message.chat.id)
        my_socium = await dbs.rings_help.get_my_socium(message.chat.id)
        for tg_id in my_socium:
            await send_message(tg_id, text_for_other_people)
            await asyncio.sleep(.05)

    return


@dp.message_handler(state=ProofObligation.list_obligation_check)
async def list_obligation_check(message: types.Message, state: FSMContext):
    in_text = message.text
    user_id = message.chat.id
    await bot.delete_message(user_id, message.message_id)

    data = await state.get_data()
    id_obligation = data["id_obligation_peoof"]

    bot_username = (await bot.me).username
    obligation = await dbs.intentions.get_intention_from_id(id_obligation)

    if _('Да, я получил') in in_text:
        user_to = await dbs.users.get_user(obligation.to_id)
        user_from = await dbs.users.get_user(obligation.from_id)
        status_from = await get_status_emoji(user_from.status)

        text_from = emojize(_("Спасибо! Участнику {} {} будет отправлено уведомление о том, что вы подтвердили "
                              "иcполнение 🤝 на сумму {}")).format(user_from.name, status_from, obligation.payment)

        text_to = _("Подтверждение") + emojize(f" {obligation.payment}👍\n")
        text_to += _("кто: ") + await get_info_text_user_for_invite(obligation.from_id, bot_username, for_me=True)
        text_to += _("\nкому: ") + await get_info_text_user_for_invite(obligation.to_id, bot_username)

        await dbs.intentions.update_status_from_id(id_obligation, status=13)
        await dbs.history_intention.create_history_intention(from_id=obligation.from_id,
                                                             to_id=obligation.to_id,
                                                             payment=obligation.payment,
                                                             user_status=obligation.user_status,
                                                             currency=obligation.currency,
                                                             from_intention=id_obligation)
        if obligation.user_status == "orange":
            await dbs.events.create_event(from_id=obligation.from_id,
                                          to_id=obligation.to_id,
                                          payment=obligation.payment,
                                          currency=obligation.currency,
                                          event_status="future_event",
                                          send=False)

        await send_message(obligation.from_id, text_to, disable_web_page_preview=True)

        await Menu.organaiser_menu.set()
        markup = await markup_organaiser_menu()

        await send_message(obligation.to_id, text_from, reply_markup=markup, disable_web_page_preview=True)

        if "red" in obligation.user_status:
            await auto_return_from_red(message, obligation, user_to)

        return
    elif _("Назад") in in_text:
        await Menu.organaiser_menu.set()
        markup = await markup_organaiser_menu()
        user = await dbs.users.get_user(message.chat.id)
        emoji_status = await get_status_emoji(user.status)
        text = _("Органайзер") + emoji_status
        await bot.send_message(message.chat.id, text, reply_markup=markup)
        return
