import asyncio
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize

from loader import dp, bot, _
from keyboards.reply.reply_kb import markup_general_menu, back_kb, start_orange_invitation_kb
from models.db_service import DBService
from states.menu_states import Menu, Invite
from utils.functions import get_all_info_text_user, is_digit, text_sum_digit, get_list_invite_for_user,\
    get_info_text_user_for_invite
from utils.util_bot import send_message

dbs = DBService()


async def start_orange_invitation(message, user_to, state: FSMContext):
    intentions_list = await dbs.intentions.get_intentions(statuses=[1, 11, 12], from_id=message.chat.id, to_id=user_to.tg_id)

    if intentions_list:
        bot_text = _('Вы уже помогаете участнику {}:'.format(user_to.name))
        for intention_one in intentions_list:
            if intention_one.status == 1:
                bot_text += "\n" + emojize(f"{intention_one.payment}:heart:")
            elif intention_one.status == 11:
                bot_text += "\n" + emojize(f"{intention_one.payment}:handshake:")
            elif intention_one.status == 12:
                bot_text += "\n" + emojize(f"{intention_one.payment}:handshake:→👍")

        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        return

    markup = await start_orange_invitation_kb(user_to)

    bot_username = (await bot.me).username
    bot_text = await get_all_info_text_user(bot_username, user_to.tg_id)
    bot_text += '\nВы можете помочь этому участнику?'

    await Invite.start_orange_invitation_check.set()
    await state.update_data(user_to_id=user_to.tg_id)

    await bot.send_message(message.chat.id, bot_text, reply_markup=markup, disable_web_page_preview=True)


@dp.message_handler(state=Invite.start_orange_invitation_check)
async def orange_invitation_check(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if emojize(':busts_in_silhouette:') in in_text:
        data = await state.get_data()
        to_id = data["user_to_id"]
        text = await get_list_invite_for_user(to_id)
        await Invite.list_invite.set()
        markup = await back_kb()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
    elif _('Нет') in in_text:
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, _('Меню'), reply_markup=markup)

    elif _('Да') in in_text:
        await Invite.input_sum_for_orange.set()
        markup = await back_kb()
        await bot.send_message(message.chat.id, _('Введите сумму помощи в €'), reply_markup=markup)

    elif _('Меню') in in_text:
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, _('Меню'), reply_markup=markup)


@dp.message_handler(state=Invite.list_invite)
async def input_sum_for_orange(message: types.Message, state: FSMContext):
    data_state = await state.get_data()
    user_to = await dbs.users.get_user(data_state["user_to_id"])

    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Назад") in in_text:
        await start_orange_invitation(message, user_to, state=state)
        return


async def send_messages_other_start_orange_invitation(intention):
    bot_username = (await bot.me).username

    to_id = intention.to_id
    from_id = intention.from_id

    # текст для получателя помощи
    text_for_to_id = emojize(f"→{intention.payment}:heart:\n")
    text_for_to_id += _("кто: ") + await get_info_text_user_for_invite(from_id, bot_username)
    text_for_to_id += _("\nкому: ") + await get_info_text_user_for_invite(to_id, bot_username, for_me=True)
    await send_message(to_id, text_for_to_id, disable_web_page_preview=True)

    # текст для всех причастных к помощи
    text_for_circle_invite = emojize(f"→{intention.payment}:heart:\n")
    text_for_circle_invite += _("кто: ") + await get_info_text_user_for_invite(from_id, bot_username)
    text_for_circle_invite += _("\nкому: ") + await get_info_text_user_for_invite(to_id, bot_username)

    list_circle_invite = await dbs.rings_help.get_my_socium_small(to_id)
    list_circle_invite.discard(from_id)

    for tg_id in list_circle_invite:
        await send_message(tg_id, text_for_circle_invite, disable_web_page_preview=True)
        await asyncio.sleep(.05)


@dp.message_handler(state=Invite.input_sum_for_orange)
async def input_sum_for_orange(message: types.Message, state: FSMContext):
    data_state = await state.get_data()
    to_id = data_state["user_to_id"]
    user_to = await dbs.users.get_user(to_id)

    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Назад") in in_text:
        await start_orange_invitation(message, user_to, state=state)
        return

    if not await is_digit(in_text):
        text = await text_sum_digit()
        await bot.send_message(message.chat.id, text)
        return

    bot_text = emojize(_('Ваше :heart: принято'))

    intention = await dbs.intentions.create_intention(from_id=message.chat.id,
                                                      to_id=to_id,
                                                      payment=int(in_text),
                                                      currency="€",
                                                      create_date=datetime.now(),
                                                      user_status="orange",
                                                      status=1)
    await dbs.rings_help.add_to_help_array(to_id, message.chat.id)

    await Menu.global_menu.set()
    markup = await markup_general_menu()

    # отправляю мэссендж себе
    await bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    # отправляю мэссендж получателю и всем причастным
    await send_messages_other_start_orange_invitation(intention)


async def start_red_invitation(message, user_to, state: FSMContext):
    intentions_list = await dbs.intentions.get_intentions(statuses=[11, 12], from_id=message.chat.id, to_id=user_to.tg_id)

    if intentions_list:
        bot_text = _('Вы уже помогаете участнику {}:'.format(user_to.name))
        for intention_one in intentions_list:
            if intention_one.status == 1:
                bot_text += "\n" + emojize(f"{intention_one.payment}:heart:")
            elif intention_one.status == 11:
                bot_text += "\n" + emojize(f"{intention_one.payment}:handshake:")
            elif intention_one.status == 12:
                bot_text += "\n" + emojize(f"{intention_one.payment}:handshake:→👍")
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        return

    markup = await start_orange_invitation_kb(user_to)

    bot_username = (await bot.me).username
    bot_text = await get_all_info_text_user(bot_username, user_to.tg_id)
    bot_text += '\nВы можете помочь этому участнику?'

    await Invite.start_red_invitation_check.set()
    await state.update_data(user_to_id=user_to.tg_id)

    await bot.send_message(message.chat.id, bot_text, reply_markup=markup, disable_web_page_preview=True)


@dp.message_handler(state=Invite.start_red_invitation_check)
async def red_invitation_check(message: types.Message):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if emojize(':busts_in_silhouette:') in in_text:
        pass
    elif _('Нет') in in_text:
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, _('Меню'), reply_markup=markup)

    elif _('Да') in in_text:
        await Invite.input_sum_for_red.set()
        markup = await back_kb()
        await bot.send_message(message.chat.id, _('Введите сумму помощи в €'), reply_markup=markup)

    elif _('Меню') in in_text:
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, _('Меню'), reply_markup=markup)


async def send_messages_other_start_red_invitention(intention):
    bot_username = (await bot.me).username

    to_id = intention.to_id
    from_id = intention.from_id

    # текст для получателя
    text_for_to_id = emojize(f"→{intention.payment}:handshake:\n")
    text_for_to_id += _("кто: ") + await get_info_text_user_for_invite(from_id, bot_username)
    text_for_to_id += _("\nкому: ") + await get_info_text_user_for_invite(to_id, bot_username, for_me=True)
    await bot.send_message(to_id, text_for_to_id, disable_web_page_preview=True)

    # текст для всех причастных к помощи
    text_for_circle_invite = emojize(f"→{intention.payment}:handshake:\n")
    text_for_circle_invite += _("кто: ") + await get_info_text_user_for_invite(from_id, bot_username)
    text_for_circle_invite += _("\nкому: ") + await get_info_text_user_for_invite(to_id, bot_username)

    list_circle_invite = await dbs.rings_help.get_my_socium_small(to_id)
    list_circle_invite.discard(from_id)

    for tg_id in list_circle_invite:
        await send_message(tg_id, text_for_circle_invite, disable_web_page_preview=True)
        await asyncio.sleep(.05)


@dp.message_handler(state=Invite.input_sum_for_red)
async def input_sum_for_red(message: types.Message, state: FSMContext):
    data_state = await state.get_data()
    to_id = data_state["user_to_id"]
    user_to = await dbs.users.get_user(to_id)

    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Назад") in in_text:
        await start_red_invitation(message, user_to, state=state)
        return

    if not await is_digit(in_text):
        text = await text_sum_digit()
        await bot.send_message(message.chat.id, text)
        return

    bot_text = emojize(_('Записано ваше :handshake:'))

    intention = await dbs.intentions.create_intention(from_id=message.chat.id,
                                                      to_id=to_id,
                                                      payment=int(in_text),
                                                      currency="€",
                                                      create_date=datetime.now(),
                                                      user_status="red",
                                                      status=11)
    await dbs.rings_help.add_to_help_array(to_id, message.chat.id)

    await Menu.global_menu.set()
    markup = await markup_general_menu()

    # отправляю мэссендж себе
    await bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    # отправляю мэссендж получателю
    await send_messages_other_start_red_invitention(intention)

    return


