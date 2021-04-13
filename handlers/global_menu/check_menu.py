from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize

from data.symbols import text_about, text_menu, text_convention, text_how_start, text_case
from loader import dp, bot, _
from keyboards.reply.reply_kb import markup_general_menu, markup_profile_menu, change_status_reply_kb, \
    log_out_from_bot, select_data_status_reply_kb, proof_change_status_reply_kb, proof_return_orange_reply_kb, back_kb, \
    requisites_menu_kb, markup_edit_profile
from models.db_service import DBService
from states.menu_states import Menu, ProfileMenu, StatusChange, DataStatusChange, AboutMe, Requisites, IntentionFrom, \
    IntentionTo, ProofObligation, BadObligation
from utils.functions import text_status_to_green, text_return_to_orange, text_for_status_menu, text_status_to_orange, \
    get_status_emoji, create_dict_intention, create_list_intention

dbs = DBService()


async def global_menu(message, state: FSMContext):
    await state.finish()
    await Menu.global_menu.set()
    markup = await markup_general_menu()
    await bot.send_message(message.chat.id, _('Меню'), reply_markup=markup)


async def intention_from_me(message, state: FSMContext):
    markup = await back_kb()
    intentions = await dbs.intentions.get_intentions(statuses=[1], from_id=message.chat.id)
    obligations = await dbs.intentions.get_intentions(statuses=[11], from_id=message.chat.id)

    dict_intention_from = await create_dict_intention(statuses=[1, 11], from_id=message.chat.id)
    list_intention = await create_list_intention(dict_intention_from, from_id=True)
    text = emojize(_("Вами записано {} :heart: и {} :handshake:\n{}\n")).format(len(intentions), len(obligations),
                                                                                list_intention)
    text += _("Введите номер записи, чтобы посмотреть подробную информацию или изменить")
    await IntentionFrom.list_intention.set()
    await state.update_data(dict_intention_from=dict_intention_from)
    await bot.send_message(message.chat.id, text, reply_markup=markup)


async def intention_to_me(message, state: FSMContext):
    markup = await back_kb()
    intentions = await dbs.intentions.get_intentions(statuses=[1], to_id=message.chat.id)
    obligations = await dbs.intentions.get_intentions(statuses=[11], to_id=message.chat.id)

    dict_intention_to = await create_dict_intention(statuses=[1, 11], to_id=message.chat.id)
    list_intention = await create_list_intention(dict_intention_to, to_id=True)
    text = emojize(_("В вашу пользу {} :heart: и {} :handshake:\n{}\n")).format(len(intentions), len(obligations),
                                                                                list_intention)
    text += _("Введите номер записи, чтобы посмотреть подробную информацию или изменить")
    await IntentionTo.list_intention.set()
    await state.update_data(dict_intention_to=dict_intention_to)
    await bot.send_message(message.chat.id, text, reply_markup=markup)


async def list_proof_obligations(message, state: FSMContext):
    markup = await back_kb()
    user_id = message.chat.id
    text_from = emojize(_(":bust_in_silhouette:->:busts_in_silhouette: Чтобы повторить уведомление об исполнении "
                          "вашего обязательства, введите номер перед записью.\n"))
    text_to = emojize(_(":busts_in_silhouette:->:bust_in_silhouette: Чтобы подтвердить исполнение обязательства в "
                        "вашу пользу, введите номер перед записью.\n"))
    text_all = ''

    dict_obligation_proof = await create_dict_intention(statuses=[12], from_id=user_id, to_id=user_id)

    count_from = 0
    count_to = 0

    for id in dict_obligation_proof:
        obligation = await dbs.intentions.get_intention_from_id(dict_obligation_proof[id])

        if obligation.from_id == user_id:
            count_from += 1
            user = await dbs.users.get_user(obligation.to_id)
            status = await get_status_emoji(user.status)
            text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

            text_from += emojize(f"{id}. {obligation.payment} :handshake: → 👍 → {text_link_user} {status} \n")
        elif obligation.to_id == user_id:
            count_to += 1
            user = await dbs.users.get_user(obligation.from_id)
            status = await get_status_emoji(user.status)
            text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

            text_to += emojize(f"{id}. {text_link_user} {status} → {obligation.payment} :handshake: → 👍\n")

    if count_from > 0:
        text_all += text_from
    if count_to > 0:
        text_all += "\n" + text_to

    text_all += _("\nВведите номер записи, чтобы посмотреть подробную информацию")

    await ProofObligation.list_obligation.set()
    await state.update_data(dict_obligation_proof=dict_obligation_proof)
    await bot.send_message(message.chat.id, text_all, reply_markup=markup)


async def list_completed_obligations(user_id):
    text = _("Ваша история исполненных обязательств:\n")

    completed_to = await dbs.history_intention.read_history_intention(to_id=user_id)
    for obligation in completed_to:
        user = await dbs.users.get_user(obligation.from_id)
        text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'
        status_emoji = await get_status_emoji(obligation.user_status)
        text += _("{}     {} {} {} → вам {}\n").format(obligation.create_date.date(),
                                                       obligation.payment,
                                                       obligation.currency,
                                                       text_link_user,
                                                       status_emoji)

    text += "\n"

    completed_from = await dbs.history_intention.read_history_intention(from_id=user_id)
    for obligation in completed_from:
        user = await dbs.users.get_user(obligation.to_id)
        text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'
        status_emoji = await get_status_emoji(obligation.user_status)
        text += _("{}     {} {} вы → {} {}\n").format(obligation.create_date.date(),
                                                      obligation.payment,
                                                      obligation.currency,
                                                      text_link_user,
                                                      status_emoji)

    return text


async def bad_history_intention(user_id, state: FSMContext):
    list_bad_obligation_from = await dbs.intentions.get_intentions(statuses=[110, 120], from_id=user_id)
    list_bad_obligation_to = await dbs.intentions.get_intentions(statuses=[110, 120], to_id=user_id)

    text_from = ''
    text_to = ''
    count = 0
    dict_bad_obligation = {}
    if len(list_bad_obligation_from) != 0:
        text_from += 'Ваши незавершенные транзакции:\n'
        for intention in list_bad_obligation_from:
            count += 1
            dict_bad_obligation[count] = intention.intention_id
            user_from = await dbs.users.get_user(intention.to_id)
            text_link_user = f'<a href="tg://user?id={user_from.tg_id}">{user_from.name}</a>'

            if intention.status == 110:
                text_from += emojize(f'{count})     {intention.create_date.date().strftime("%m-%Y")} вы не исполнили {intention.payment}:handshake: в пользу {text_link_user}\n')
            else:
                text_from += emojize(f'{count})     {intention.create_date.date().strftime("%m-%Y")}     {intention.payment} :handshake: → 👍 вы ждете подтверждения от {text_link_user}\n')

    if len(list_bad_obligation_to) != 0:
        text_to += 'Незавершенные транзакции в вашу пользу:\n'
        for intention in list_bad_obligation_to:
            count += 1
            dict_bad_obligation[count] = intention.intention_id
            user_to = await dbs.users.get_user(intention.from_id)
            text_link_user = f'<a href="tg://user?id={user_to.tg_id}">{user_to.name}</a>'

            if intention.status == 110:
                text_to += emojize(f'{count})     {intention.create_date.date().strftime("%m-%Y")}     {text_link_user} не исполнил {intention.payment} :handshake: в вашу пользу\n')
            else:
                text_to += emojize(f'{count})     {intention.create_date.date().strftime("%m-%Y")}     {intention.payment} :handshake: →  👍 {text_link_user} ждет подтверждения исполнения от вас\n')

    bot_text = f'{text_from}\n\n\
{text_to}\n'
    bot_text += "Введите номер записи, чтобы посмотреть подробную информацию"

    markup = await back_kb()

    await BadObligation.list_obligation.set()
    await state.update_data(dict_bad_obligation=dict_bad_obligation)
    await bot.send_message(user_id, bot_text, reply_markup=markup)


@dp.message_handler(state=Menu.organaiser_menu)
async def organaiser_menu_check(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if emojize(":bust_in_silhouette:→:busts_in_silhouette:") in in_text:
        await intention_from_me(message, state)
        return

    elif emojize(":busts_in_silhouette:→:bust_in_silhouette:") in in_text:
        await intention_to_me(message, state)
        return

    elif emojize(":handshake:→👍\n0→:bust_in_silhouette:→0") in in_text:
        text = emojize(_("У вас нет неподтвержденных :handshake:"))
        await bot.send_message(message.chat.id, text)
        return
    elif emojize("Архив 👍\n0/0→:bust_in_silhouette:→0/0") in in_text:
        text = emojize(_("У вас нет исполненных :handshake:"))
        await bot.send_message(message.chat.id, text)
        return
    elif emojize(":handshake:→👍") in in_text:
        await list_proof_obligations(message, state)
        return

    elif emojize(_("Архив 👍")) in in_text:
        text = await list_completed_obligations(message.chat.id)
        await bot.send_message(message.chat.id, text)
        return
    elif emojize(":hourglass:\n0") in in_text:
        text = _("У вас нет незавершенных транзакций")
        await bot.send_message(message.chat.id, text)
        return
    elif emojize(":hourglass:") in in_text:
        await bad_history_intention(message.chat.id, state)
        return
    elif _('Меню') in in_text:
        await global_menu(message, state)
        return


async def edit_lang_user(message: types.Message, lang):
    await dbs.users.set_language(lang)
    markup = await markup_profile_menu(lang)
    await bot.send_message(message.chat.id, _("Ваш язык был изменен", locale=lang), reply_markup=markup)


@dp.message_handler(state=Menu.profile_menu)
async def profile_menu_check(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)
    user = await dbs.users.get_user(message.chat.id)
    if _("Статус") in in_text:
        await ProfileMenu.status.set()
        markup = await select_data_status_reply_kb()
        text = await text_for_status_menu(message.chat.id)
        await bot.send_message(message.chat.id, text, reply_markup=markup)
    elif _("Обо мне") in in_text:
        await AboutMe.check_input.set()
        markup = await markup_edit_profile()
        if user.link:
            link = user.link
        else:
            link = 'не заданы'

        bot_text = _('Текущее имя пользователя: {}\n').format(user.name)
        bot_text += _('Текущая ссылка и описание: {}').format(link)
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    elif _("Реквизиты") in in_text:
        requisites = await dbs.requisites.get_all_requisites()
        if requisites:
            text = _('Выберите реквизиты для редактирования')
        else:
            text = _('Вы еще не задали реквизиты')

        await Requisites.requisites_menu.set()
        markup = await requisites_menu_kb()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
    elif _("Выйти") in in_text:
        await ProfileMenu.log_out.set()
        markup = await log_out_from_bot()
        await bot.send_message(message.chat.id, _("Вы собираетесь выйти из бота и удалить свой профиль?"),
                               reply_markup=markup)
    elif "RU→" in in_text:
        await edit_lang_user(message, "en")
    elif "ENG→" in in_text:
        await edit_lang_user(message, "ru")
    elif _('Меню') in in_text:
        await global_menu(message, state)

    return


@dp.message_handler(state=ProfileMenu.log_out)
async def profile_menu_log_out_check(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Да, удалить профиль") in in_text:
        # await dbs.users.delete_user(message.chat.id)
        markup = types.ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, _("Вы удалили свой профиль"), reply_markup=markup)
        await state.finish()
    elif _("Нет, я остаюсь") in in_text:
        await Menu.profile_menu.set()
        markup = await markup_profile_menu()
        await bot.send_message(message.chat.id, _("Спасибо, что остаетесь!"), reply_markup=markup)


@dp.message_handler(state=ProfileMenu.status)
async def select_data_status_check(message: types.Message):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Изменить данные") in in_text:
        user = await dbs.users.get_user(message.chat.id)
        markup = await proof_change_status_reply_kb()
        status_emoji = await get_status_emoji(user.status)
        text = status_emoji + _(
            "Вы собираетесь изменить данные статуса. \nПожалуйста, подтвердите действие")

        if user.status == 'orange':
            await DataStatusChange.proof_change_orange.set()
            await bot.send_message(message.chat.id, text, reply_markup=markup)
        elif 'red' in user.status:
            await DataStatusChange.proof_change_red.set()
            await bot.send_message(message.chat.id, text, reply_markup=markup)

    elif _("Изменить статус") in in_text:
        await StatusChange.change_status.set()
        markup = await change_status_reply_kb()
        await bot.send_message(message.chat.id, _("Выберите статус"), reply_markup=markup)

    elif _("Назад") in in_text:
        await Menu.profile_menu.set()
        markup = await markup_profile_menu()
        await bot.send_message(message.chat.id, _("Профиль"), reply_markup=markup)


@dp.message_handler(state=StatusChange.change_status)
async def profile_menu_status_check(message: types.Message):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if emojize(":sos:") in in_text:
        text = emojize(_("Вы собираетесь сменить статус на :sos:\nПожалуйста подтвердите смену статуса"))
        markup = await proof_change_status_reply_kb()
        await StatusChange.proof_change_red.set()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
        return

    elif emojize(":white_check_mark:") in in_text:
        await StatusChange.proof_change_green.set()
        markup = await proof_change_status_reply_kb()
        text = await text_status_to_green()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
        return

    elif (_("Вернуться к ") + emojize(":high_brightness:")) in in_text:
        await StatusChange.return_to_orange.set()
        markup = await proof_return_orange_reply_kb()

        sum = await dbs.statuses.get_status(message.chat.id, "orange")
        text = await text_return_to_orange(sum.payment)
        await bot.send_message(message.chat.id, text, reply_markup=markup)
        return

    elif emojize(":high_brightness:") in in_text:
        await StatusChange.proof_change_orange.set()
        markup = await proof_change_status_reply_kb()
        text = await text_status_to_orange()
        await bot.send_message(message.chat.id, text, reply_markup=markup)
        return
    elif _("Назад") in in_text:
        await ProfileMenu.status.set()
        markup = await select_data_status_reply_kb()
        text = await text_for_status_menu(message.chat.id)
        await bot.send_message(message.chat.id, text, reply_markup=markup)
        return


@dp.message_handler(state=Menu.faq_menu)
async def faq_menu_check(message: types.Message, state: FSMContext):
    in_text = message.text
    await bot.delete_message(message.chat.id, message.message_id)

    if _("Про бота") in in_text:
        text = await text_about()
        await bot.send_message(message.chat.id, text, disable_web_page_preview=True)
    elif _("Описание меню") in in_text:
        text = await text_menu()
        await bot.send_message(message.chat.id, text, disable_web_page_preview=True)
    elif _("Условные обозначения") in in_text:
        text = await text_convention()
        await bot.send_message(message.chat.id, text, disable_web_page_preview=True)
    elif _("Как начать пользоваться") in in_text:
        text = await text_how_start()
        await bot.send_message(message.chat.id, text, disable_web_page_preview=True)
    elif _("Возможные кейсы") in in_text:
        text = await text_case()
        await bot.send_message(message.chat.id, text, disable_web_page_preview=True)
    elif _('Меню') in in_text:
        await global_menu(message, state)

    return
