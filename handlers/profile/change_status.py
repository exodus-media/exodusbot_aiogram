import asyncio
from datetime import date, timedelta

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize


from loader import dp, bot, _
from keyboards.reply.reply_kb import change_status_reply_kb, final_proof_change_status_reply_kb, markup_general_menu
from models.db_service import DBService
from states.menu_states import Menu, StatusChange
from utils.functions import text_input_sum_orange, is_digit, text_sum_digit, get_all_info_text_user, get_status_emoji, \
    send_notify_for_auto_end_red
from utils.util_bot import send_message

dbs = DBService()


async def send_notify_all_user(user_id, text, status):
    user = await dbs.users.get_user(user_id)
    bot_username = (await bot.me).username
    emoji_status = await get_status_emoji(status)
    text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

    text_for_other_people = f"{text_link_user} {text} {emoji_status}\n"
    text_for_other_people += await get_all_info_text_user(bot_username, user_id)

    my_socium = await dbs.rings_help.get_my_socium(user_id)
    for tg_id in my_socium:
        await send_message(tg_id, text_for_other_people, disable_web_page_preview=True)
        await asyncio.sleep(.05)


@dp.message_handler(state=StatusChange.proof_change_green)
async def change_status_to_green(message: types.Message):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Да, изменить") in in_text:
        await dbs.users.update_user(message.chat.id, status="green")

        await dbs.intentions.update_intention_status_with_tg_id(old_status=1, new_status=0, to_id=message.chat.id)
        await dbs.intentions.update_intention_status_with_tg_id(old_status=11, new_status=110, to_id=message.chat.id)
        await dbs.intentions.update_intention_status_with_tg_id(old_status=12, new_status=120, to_id=message.chat.id)
        await dbs.intentions.update_intention_status_with_tg_id(old_status=13, new_status=0, to_id=message.chat.id)

        await send_notify_all_user(message.chat.id, _("сменил статус на"), "green")

        text = emojize(_("Статус изменен на :white_check_mark:"))
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
    elif _("Нет, вернуться назад") in in_text:
        await StatusChange.change_status.set()
        markup = await change_status_reply_kb()
        await bot.send_message(message.chat.id, _("Выберите статус"), reply_markup=markup)


@dp.message_handler(state=StatusChange.proof_change_red)
async def change_status_to_red(message: types.Message):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Да, изменить") in in_text:
        text = _("Введите сумму в €, которая вам необходима")
        await StatusChange.input_sum_red.set()
        markup = types.ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
    elif _("Нет, вернуться назад") in in_text:
        await StatusChange.change_status.set()
        markup = await change_status_reply_kb()
        await bot.send_message(message.chat.id, _("Выберите статус"), reply_markup=markup)


@dp.message_handler(state=StatusChange.input_sum_red)
async def input_sum_red(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if not await is_digit(in_text):
        text = await text_sum_digit()
        await bot.send_message(message.chat.id, text)
        return

    await StatusChange.input_days_red.set()
    await state.update_data(red_sum=in_text)

    text = emojize(_(":sos: Введите цифрами число дней, за которые вам необходимо набрать эту сумму"))
    await bot.send_message(message.chat.id, text)


@dp.message_handler(state=StatusChange.input_days_red)
async def input_days_red(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if not await is_digit(in_text):
        text = await text_sum_digit()
        await bot.send_message(message.chat.id, text)
        return

    await StatusChange.final_input_red.set()
    await state.update_data(red_days=in_text)

    data_state = await state.get_data()

    text = emojize(_("""Пожалуйста проверьте введенные данные:    
Статус: :sos:
В течении: {} дней
Необходимая сумма: {}€""".format(in_text, data_state["red_sum"])))
    text += _("""\n\nВы хотите изменить свой статус и опубликовать эти данные?    
Все пользователи, которые связаны с вами внутри Эксодус бота, получат уведомление.""")
    markup = await final_proof_change_status_reply_kb()
    await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(state=StatusChange.final_input_red)
async def final_input_red(message: types.Message, state: FSMContext):

    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Сохранить") in in_text:
        data_state = await state.get_data()
        user = await dbs.users.get_user(message.chat.id)

        await dbs.users.update_user(message.chat.id, status="red"+user.status)
        await dbs.statuses.update_status(message.chat.id, "red",
                                       payment=data_state['red_sum'],
                                       finish_date=date.today() + timedelta(days=int(data_state['red_days'])),
                                       create_date=date.today()
                                       )
        await dbs.intentions.update_active(to_id=message.chat.id, user_status="orange", active=0)

        await send_notify_all_user(message.chat.id, _("сменил статус на"), "red")

        text = _("Настройки сохранены\n")
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
    elif _("Отмена") in in_text:
        await StatusChange.change_status.set()
        markup = await change_status_reply_kb()
        await bot.send_message(message.chat.id, _("Выберите статус"), reply_markup=markup)


@dp.message_handler(state=StatusChange.proof_change_orange)
async def change_status_to_orange(message: types.Message):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Да, изменить") in in_text:
        text = _("Какая сумма вам необходима на базовые нужды в €?")
        await StatusChange.input_sum_orange.set()
        markup = types.ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
    elif _("Нет, вернуться назад") in in_text:
        await StatusChange.change_status.set()
        markup = await change_status_reply_kb()
        await bot.send_message(message.chat.id, _("Выберите статус"), reply_markup=markup)


@dp.message_handler(state=StatusChange.input_sum_orange)
async def input_sum_orange(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if not await is_digit(in_text):
        text = await text_sum_digit()
        await bot.send_message(message.chat.id, text)
        return

    await StatusChange.final_input_orange.set()
    await state.update_data(orange_sum=in_text)

    text = await text_input_sum_orange(in_text)

    markup = await final_proof_change_status_reply_kb()
    await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(state=StatusChange.final_input_orange)
async def final_input_orange(message: types.Message, state: FSMContext):

    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Сохранить") in in_text:
        data_state = await state.get_data()

        await Menu.profile_menu.set()
        await dbs.users.update_user(message.chat.id, status="orange")
        await dbs.statuses.update_status(message.chat.id, "orange", payment=int(data_state['orange_sum']))

        await send_notify_all_user(message.chat.id, _("сменил статус на"), "orange")

        text = _("Настройки сохранены\n")
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
    elif _("Отмена") in in_text:
        await StatusChange.change_status.set()
        markup = await change_status_reply_kb()
        await bot.send_message(message.chat.id, _("Выберите статус"), reply_markup=markup)


@dp.message_handler(state=StatusChange.return_to_orange)
async def return_to_orange(message: types.Message):

    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Сохранить") in in_text:
        await Menu.profile_menu.set()
        await dbs.users.update_user(message.chat.id, status="orange")

        await dbs.intentions.update_intention_status_with_tg_id(old_status=11, new_status=110,
                                                                to_id=message.chat.id, user_status='red')
        await dbs.intentions.update_intention_status_with_tg_id(old_status=12, new_status=120,
                                                                to_id=message.chat.id, user_status='red')
        await dbs.intentions.update_intention_status_with_tg_id(old_status=13, new_status=0,
                                                                to_id=message.chat.id, user_status='red')

        await dbs.intentions.update_active(to_id=message.chat.id, user_status="orange", active=1)

        text = _("Настройки сохранены\n")
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, text, reply_markup=markup)

        # отправляем тому, кто участвует в помощи
        await send_notify_all_user(message.chat.id, _("возвращается к"), "orange")
        text_for_other_people = await send_notify_for_auto_end_red(message.chat.id)
        my_socium = await dbs.rings_help.get_my_socium(message.chat.id)
        for tg_id in my_socium:
            await send_message(tg_id, text_for_other_people)
            await asyncio.sleep(.05)

        return

    elif _("Отмена") in in_text:
        await StatusChange.change_status.set()
        markup = await change_status_reply_kb()
        await bot.send_message(message.chat.id, _("Выберите статус"), reply_markup=markup)
        return
