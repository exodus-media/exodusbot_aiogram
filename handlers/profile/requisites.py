from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.reply.reply_kb import markup_profile_menu, requisites_add_check_kb, requisites_menu_kb, \
    requisites_edit_kb
from loader import dp, _, bot
from models.db_service import DBService
from states.menu_states import Requisites, Menu
from utils.functions import is_it_requisites

dbs = DBService()


@dp.message_handler(state=Requisites.requisites_menu)
async def requisites_menu_check(message: types.Message, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)
    requisites = await dbs.requisites.get_all_requisites()
    req = await is_it_requisites(message.text, requisites)
    if req:
        await Requisites.edit_requisites.set()
        text = _bot_text = _('Название: {}\n\
Значение: {}\n').format(req.name, req.value)
        markup = await requisites_edit_kb()
        await state.update_data(req_id=req.id)
        await bot.send_message(message.chat.id, text, reply_markup=markup)

    elif _('Добавить реквизиты') in message.text:
        await Requisites.add_requisites_name.set()
        text = _('Введите название реквизита (например "Карта Сбербанка", "Счет в SKB" или "PayPal")')
        markup = types.ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, text, reply_markup=markup)

    elif _('Назад') in message.text:
        await Menu.profile_menu.set()
        markup = await markup_profile_menu()
        await bot.send_message(message.chat.id, _("Профиль"), reply_markup=markup)


@dp.message_handler(state=Requisites.add_requisites_name)
async def requisites_add_name(message: types.Message, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)
    await state.update_data(requisites_name=message.text)
    await Requisites.add_requisites_check.set()
    text = _('Введите только номер счета, карты или идентификатор')
    markup = types.ReplyKeyboardRemove()
    await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(state=Requisites.add_requisites_check)
async def requisites_add_check(message: types.Message, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)
    await Requisites.add_requisites_finish.set()
    await state.update_data(requisites_value=message.text)
    state_data = await state.get_data()
    text = _('Название: {}\n\
Значение: {}\n\
Данные введены верно?').format(state_data['requisites_name'], state_data['requisites_value'])
    markup = await requisites_add_check_kb()

    await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(state=Requisites.add_requisites_finish)
async def requisites_add_finish(message: types.Message, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)

    if _('Да') == message.text:
        state_data = await state.get_data()
        await dbs.requisites.create_requisite(state_data['requisites_name'], state_data['requisites_value'])
        await Requisites.requisites_menu.set()
        markup = await requisites_menu_kb()
        text = _('Выберите реквизиты для редактирования:')
        await bot.send_message(message.chat.id, text, reply_markup=markup)

    elif _('Нет') in message.text:
        await Requisites.add_requisites_name.set()
        text = _('Введите название реквизита (например "Карта Сбербанка", "Счет в SKB" или "PayPal")')
        await bot.send_message(message.chat.id, text)

    elif _('Да, сделать реквизитами по умолчанию') in message.text:
        state_data = await state.get_data()
        new_req = await dbs.requisites.create_requisite(state_data['requisites_name'], state_data['requisites_value'])
        await dbs.requisites.set_default_requisite(new_req.id)
        await Requisites.requisites_menu.set()
        markup = await requisites_menu_kb()
        text = _('Выберите реквизиты для редактирования:')
        await bot.send_message(message.chat.id, text, reply_markup=markup)

    elif _('Отмена') in message.text:
        await Menu.profile_menu.set()
        markup = await markup_profile_menu()
        await bot.send_message(message.chat.id, _("Профиль"), reply_markup=markup)


@dp.message_handler(state=Requisites.edit_requisites)
async def edit_requisites(message: types.Message, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)

    if 'Редактировать данные' in message.text:
        await Requisites.edit_requisites_name.set()
        text = _('Введите название реквизита (например "Карта Сбербанка", "Счет в SKB" или "PayPal")')
        markup = types.ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, text, reply_markup=markup)

    elif 'Сделать реквизитами по умолчанию' in message.text:
        state_date = await state.get_data()
        await dbs.requisites.set_default_requisite(state_date['req_id'])
        await Requisites.requisites_menu.set()
        markup = await requisites_menu_kb()
        text = _('Выберите реквизиты для редактирования:')
        await bot.send_message(message.chat.id, text, reply_markup=markup)

    elif 'Удалить' in message.text:
        state_date = await state.get_data()
        await dbs.requisites.delete_requisites_and_set_default(state_date['req_id'])
        await Requisites.requisites_menu.set()
        markup = await requisites_menu_kb()
        text = _('Выберите реквизиты для редактирования:')
        await bot.send_message(message.chat.id, text, reply_markup=markup)

    elif 'Назад' in message.text:
        await Requisites.requisites_menu.set()
        markup = await requisites_menu_kb()
        text = _('Выберите реквизиты для редактирования:')
        await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(state=Requisites.edit_requisites_name)
async def edit_requisites_name(message: types.Message, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)
    await state.update_data(requisites_name=message.text)
    await Requisites.edit_requisites_check.set()
    text = _('Введите только номер счета, карты или идентификатор')
    markup = types.ReplyKeyboardRemove()
    await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(state=Requisites.edit_requisites_check)
async def edit_requisites_check(message: types.Message, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)
    await Requisites.edit_requisites_finish.set()
    await state.update_data(requisites_value=message.text)
    state_data = await state.get_data()
    text = _('Название: {}\n\
Значение: {}\n\
Данные введены верно?').format(state_data['requisites_name'], state_data['requisites_value'])
    markup = await requisites_add_check_kb()

    await bot.send_message(message.chat.id, text, reply_markup=markup)


@dp.message_handler(state=Requisites.edit_requisites_finish)
async def edit_requisites_finish(message: types.Message, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)

    if _('Да') == message.text:
        state_data = await state.get_data()
        await dbs.requisites.update_requisites(req_id=state_data['req_id'],
                                               name=state_data['requisites_name'],
                                               value=state_data['requisites_value'])
        await Menu.profile_menu.set()
        markup = await markup_profile_menu()
        await bot.send_message(message.chat.id, _("Профиль"), reply_markup=markup)

    elif _('Нет') in message.text:
        await Requisites.edit_requisites_name.set()
        text = _('Введите название реквизита (например "Карта Сбербанка", "Счет в SKB" или "PayPal")')
        await bot.send_message(message.chat.id, text)

    elif _('Да, сделать реквизитами по умолчанию') in message.text:
        state_data = await state.get_data()
        await dbs.requisites.update_requisites(req_id=state_data['req_id'],
                                               name=state_data['requisites_name'],
                                               value=state_data['requisites_value'])
        await dbs.requisites.set_default_requisite(state_data['req_id'])
        await Requisites.requisites_menu.set()
        markup = await requisites_menu_kb()
        text = _('Выберите реквизиты для редактирования:')
        await bot.send_message(message.chat.id, text, reply_markup=markup)

    elif _('Отмена') in message.text:
        await Requisites.requisites_menu.set()
        markup = await requisites_menu_kb()
        text = _('Выберите реквизиты для редактирования:')
        await bot.send_message(message.chat.id, text, reply_markup=markup)
