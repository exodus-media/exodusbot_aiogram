from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize

from loader import dp, bot, _
from keyboards.reply.reply_kb import markup_organaiser_menu
from models.db_service import DBService
from states.menu_states import Menu, BadObligation
from utils.functions import is_digit, text_sum_digit, get_status_emoji, check_number_dict
from utils.util_bot import send_message

dbs = DBService()


@dp.message_handler(state=BadObligation.list_obligation)
async def check_dict_bad_obligation(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)
    user_id = message.chat.id

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
    dict_bad_obligation = data["dict_bad_obligation"]

    if in_text not in dict_bad_obligation:
        text = await check_number_dict()
        await bot.send_message(message.chat.id, text)
        return

    id_obligation = dict_bad_obligation[in_text]

    obligation = await dbs.intentions.get_intention_from_id(id_obligation)
    user_to = await dbs.users.get_user(obligation.to_id)
    text_link_user_to = f'<a href="tg://user?id={user_to.tg_id}">{user_to.name}</a>'

    user_from = await dbs.users.get_user(obligation.from_id)
    text_link_user_from = f'<a href="tg://user?id={user_from.tg_id}">{user_from.name}</a>'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    if user_id == user_from.tg_id:
        if obligation.status == 110:
            text_obligation = emojize(
                f'У вас :handshake: на {obligation.payment} {obligation.currency} перед {text_link_user_to}\n')
            btn1 = _('Я отправил деньги')
            btn2 = _('Назад')
            markup.row(btn1, btn2)
        else:
            text_obligation = emojize(
                f'{text_link_user_to} не подтвердил исполненное :handshake: на {obligation.payment} {obligation.currency}\n')
            btn1 = _('Попросить подтверждение')
            btn2 = _('Назад')
            markup.row(btn1, btn2)

    elif user_id == user_to.tg_id:
        if obligation.status == 110:
            text_obligation = emojize(f"{text_link_user_from} → :handshake: {obligation.payment}\n")
            btn1 = _('Запрос на исполнение')
            # btn2 = _('Простить обязательство')
            btn3 = _('Назад')
            markup.row(btn1, btn3)
        else:
            text_obligation = emojize(
                f'Вы не подтвердили исполнение :handshake: на {obligation.payment} {obligation.currency} от {text_link_user_from}\n')
            btn1 = _('Подтвердить исполнение')
            btn2 = _('Назад')
            markup.row(btn1, btn2)

    await BadObligation.list_obligation_check.set()
    await state.update_data(id_bad_obligation=id_obligation)

    await bot.send_message(user_id, text_obligation, reply_markup=markup)


@dp.message_handler(state=BadObligation.list_obligation_check)
async def organaiser_menu_check(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    data = await state.get_data()
    id_bad_obligation = data["id_bad_obligation"]

    obligation = await dbs.intentions.get_intention_from_id(id_bad_obligation)
    user_to = await dbs.users.get_user(obligation.to_id)
    text_link_user_to = f'<a href="tg://user?id={user_to.tg_id}">{user_to.name}</a>'

    user_from = await dbs.users.get_user(obligation.from_id)
    text_link_user_from = f'<a href="tg://user?id={user_from.tg_id}">{user_from.name}</a>'

    if _('Я отправил деньги') in in_text:
        bot_text = _("Спасибо, что исполнили обязательство")
        await dbs.intentions.update_status_from_id(intention_id=id_bad_obligation, status=120)

        await Menu.organaiser_menu.set()
        markup = await markup_organaiser_menu()
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)

        await send_message(obligation.to_id,
                               emojize(_("В вашу пользу исполнили архивное {} :handshake:, проверьте соответвующее меню")).format(obligation.payment))
        return

    elif _("Попросить подтверждение") in in_text:

        await send_message(obligation.to_id,
                         emojize(_(
                             "{} просит подтвердить исполнение архивного {} :handshake: → 👍")).format(text_link_user_from, obligation.payment))

        await Menu.organaiser_menu.set()
        markup = await markup_organaiser_menu()
        bot_text = emojize(_("Участнику {} отправлен запрос на подтверждение {} :handshake:")).format(text_link_user_to, obligation.payment)
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        return
    elif _("Запрос на исполнение") in in_text:

        status = await get_status_emoji(user_to.status)
        await send_message(obligation.from_id, emojize(_("Пожалуйста, исполните {}:handshake: → {} {} в архиве :hourglass:")).format(obligation.payment, text_link_user_to, status))

        await Menu.organaiser_menu.set()
        markup = await markup_organaiser_menu()
        bot_text = emojize(_("Участнику {} отправлен запрос на исполнение {} :handshake:")).format(text_link_user_from, obligation.payment)
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        return

    elif _("Простить обязательство") in in_text:

        await dbs.intentions.update_status_from_id(intention_id=id_bad_obligation, status=0)
        await send_message(obligation.from_id,
                         emojize(_("{} простил вам {} :handshake:")).format(text_link_user_to, obligation.payment))

        await Menu.organaiser_menu.set()
        markup = await markup_organaiser_menu()
        bot_text = emojize(_("Вы простили {} :handshake: от участника {}")).format(obligation.payment, text_link_user_from)
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        return

    elif _("Подтвердить исполнение") in in_text:

        await dbs.intentions.update_status_from_id(intention_id=id_bad_obligation, status=130)
        await dbs.history_intention.create_history_intention(from_id=obligation.from_id,
                                                             to_id=obligation.to_id,
                                                             payment=obligation.payment,
                                                             user_status=obligation.user_status,
                                                             currency=obligation.currency,
                                                             from_intention=id_bad_obligation)

        await bot.send_message(obligation.from_id,
                         emojize(_("{} подтвердил исполнение архивного {} :handshake:")).format(text_link_user_to, obligation.payment))

        await Menu.organaiser_menu.set()
        markup = await markup_organaiser_menu()
        bot_text = emojize(_("Вы подтвердили исполнение {} :handshake: от участника {}")).format(obligation.payment, text_link_user_from)
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        return

    elif _("Назад") in in_text:
        await Menu.organaiser_menu.set()
        markup = await markup_organaiser_menu()
        user = await dbs.users.get_user(message.chat.id)
        emoji_status = await get_status_emoji(user.status)
        text = _("Органайзер") + emoji_status
        await bot.send_message(message.chat.id, text, reply_markup=markup)
        return
