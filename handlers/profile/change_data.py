from datetime import date, timedelta

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize


from loader import dp, bot, _
from keyboards.reply.reply_kb import final_proof_change_status_reply_kb, markup_general_menu, \
    select_data_status_reply_kb
from models.db_service import DBService
from states.menu_states import Menu, StatusChange, DataStatusChange, ProfileMenu
from utils.functions import text_input_sum_orange, text_for_status_menu, is_digit, text_sum_digit

dbs = DBService()


@dp.message_handler(state=DataStatusChange.proof_change_orange)
async def proof_change_orange_data(message: types.Message):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Да, изменить") in in_text:
        text = _("Какая сумма вам необходима на базовые нужды в €?")
        await DataStatusChange.input_sum_orange.set()
        markup = types.ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
    elif _("Нет, вернуться назад") in in_text:
        await ProfileMenu.status.set()
        markup = await select_data_status_reply_kb()
        text = await text_for_status_menu(message.chat.id)
        await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(state=DataStatusChange.input_sum_orange)
async def input_sum_orange_data(message: types.Message, state: FSMContext):
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
async def final_input_orange_data(message: types.Message, state: FSMContext):

    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Сохранить") in in_text:
        data_state = await state.get_data()

        await Menu.profile_menu.set()
        await dbs.users.update_user(message.chat.id, status="orange")
        await dbs.statuses.update_status(message.chat.id, "orange", payment=int(data_state['orange_sum']))

        text = _("Настройки сохранены\n")
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
    elif _("Отмена") in in_text:
        await ProfileMenu.status.set()
        markup = await select_data_status_reply_kb()
        text = await text_for_status_menu(message.chat.id)
        await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(state=DataStatusChange.proof_change_red)
async def change_status_to_red_data(message: types.Message):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Да, изменить") in in_text:
        text = emojize(_(":sos: Введите сумму в €, которая вам необходима"))
        await DataStatusChange.input_sum_red.set()
        markup = types.ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
    elif _("Нет, вернуться назад") in in_text:
        await ProfileMenu.status.set()
        markup = await select_data_status_reply_kb()
        text = await text_for_status_menu(message.chat.id)
        await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(state=DataStatusChange.input_sum_red)
async def input_sum_red_data(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if not await is_digit(in_text):
        text = await text_sum_digit()
        await bot.send_message(message.chat.id, text)
        return

    await DataStatusChange.input_days_red.set()
    await state.update_data(red_sum=in_text)

    text = emojize(_(":sos: Введите цифрами число дней, за которые вам необходимо набрать эту сумму"))
    await bot.send_message(message.chat.id, text)


@dp.message_handler(state=DataStatusChange.input_days_red)
async def input_days_red_data(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if not await is_digit(in_text):
        text = await text_sum_digit()
        await bot.send_message(message.chat.id, text)
        return

    await DataStatusChange.final_input_red.set()
    await state.update_data(red_days=in_text)

    data_state = await state.get_data()

    text = emojize(_("""Пожалуйста проверьте введенные данные:    
Статус: :sos:
В течении: {} дней
Необходимая сумма: {} €""".format(in_text, data_state["red_sum"])))
    text += _("""\n\nВы хотите изменить свой статус и опубликовать эти данные?    
Все пользователи, которые связаны с вами внутри Эксодус бота, получат уведомление.""")
    markup = await final_proof_change_status_reply_kb()
    await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(state=DataStatusChange.final_input_red)
async def final_input_red_data(message: types.Message, state: FSMContext):

    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Сохранить") in in_text:
        data_state = await state.get_data()

        await dbs.statuses.update_status(message.chat.id, "red",
                                       payment=data_state['red_sum'],
                                       finish_date=date.today() + timedelta(days=int(data_state['red_days'])),
                                       create_date=date.today()
                                       )

        text = _("Настройки сохранены\n")
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
    elif _("Отмена") in in_text:
        await ProfileMenu.status.set()
        markup = await select_data_status_reply_kb()
        text = await text_for_status_menu(message.chat.id)
        await bot.send_message(message.chat.id, text, reply_markup=markup)