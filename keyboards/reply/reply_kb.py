from aiogram import types
from aiogram.utils.emoji import emojize

from data.config import ADMIN
from loader import _
from models.db_service import DBService
from utils.functions import get_status_emoji, get_intentions_count_sum_to, get_intentions_count_sum_from, \
    get_all_obligations_count_sum_to, get_all_obligations_count_sum_from, get_all_obligations_completed_from, \
    get_all_obligations_completed_to

dbs = DBService()


async def markup_general_menu(lang=None):
    user_from_tg = types.User.get_current()
    user_from_db = await dbs.users.get_user(user_from_tg.id)

    status = await get_status_emoji(user_from_db.status)
    markup_general_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    if lang:
        btn1 = emojize(_(":spiral_calendar_pad:\nОрганайзер", locale=lang))
        btn2 = emojize(":bust_in_silhouette:") + status + "\n" + _("Профиль", locale=lang)
        btn3 = emojize(_(":busts_in_silhouette:\nУчастники", locale=lang))
        btn4 = emojize(":question: FAQ")

        markup_general_menu.add(btn1, btn2)
        markup_general_menu.add(btn3, btn4)

        if user_from_tg.id == ADMIN:
            btn5 = _("Администратор",  locale=lang)
            markup_general_menu.add(btn5)

    else:
        btn1 = emojize(_(":spiral_calendar_pad:\nОрганайзер"))
        btn2 = emojize(":bust_in_silhouette:") + status + "\n" + _("Профиль")
        btn3 = emojize(_(":busts_in_silhouette:\nУчастники"))
        btn4 = emojize(":question: FAQ")

        markup_general_menu.add(btn1, btn2)
        markup_general_menu.add(btn3, btn4)

        if user_from_tg.id == ADMIN:
            btn5 = _("Администратор")
            markup_general_menu.add(btn5)

    return markup_general_menu


async def markup_organaiser_menu():
    user_id = types.User.get_current()

    markup_organaiser_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    intentions_from_count, intentions_from_sum = await get_intentions_count_sum_from(from_id=user_id)
    obligations_from_count, obligations_from_sum = await get_all_obligations_count_sum_from(from_id=user_id, statuses=[11])
    proof_obligation_from_count, proof_obligation_from_sum = await get_all_obligations_count_sum_from(from_id=user_id,
                                                                                                  statuses=[12])
    completed_obligation_from_count, completed_obligation_from_sum = await get_all_obligations_completed_from(
        from_id=user_id)
    archive_obligation_from_count, archive_obligation_from_sum = await get_all_obligations_count_sum_from(from_id=user_id,
                                                                                                      statuses=[110,
                                                                                                                120])

    intentions_to_count, intentions_to_sum = await get_intentions_count_sum_to(to_id=user_id)
    obligations_to_count, obligations_to_sum = await get_all_obligations_count_sum_to(to_id=user_id, statuses=[11])
    proof_obligation_to_count, proof_obligation_to_sum = await get_all_obligations_count_sum_to(to_id=user_id,
                                                                                            statuses=[12])
    completed_obligation_to_count, completed_obligation_to_sum = await get_all_obligations_completed_to(to_id=user_id)
    archive_obligation_to_count, archive_obligation_to_sum = await get_all_obligations_count_sum_to(to_id=user_id,
                                                                                                statuses=[110, 120])

    count_bad_obligation = archive_obligation_from_count + archive_obligation_to_count

    btn1 = emojize(
        f":bust_in_silhouette:→:busts_in_silhouette:\n"
        f"{intentions_from_count}/{intentions_from_sum}:heart:|{obligations_from_count}/{obligations_from_sum}:handshake:")
    btn2 = emojize(
        f":busts_in_silhouette:→:bust_in_silhouette:\n"
        f"{intentions_to_count}/{intentions_to_sum}:heart:|{obligations_to_count}/{obligations_to_sum}:handshake:")
    btn3 = emojize(f":handshake:→👍\n{proof_obligation_to_count}→:bust_in_silhouette:→{proof_obligation_from_count}")
    btn4 = emojize(_("Архив 👍\n") +
        f"{completed_obligation_to_count}/{completed_obligation_to_sum}→:bust_in_silhouette:→"
        f"{completed_obligation_from_count}/{completed_obligation_from_sum}")
    btn5 = emojize(_("Архив :hourglass:\n{}")).format(count_bad_obligation)
    btn6 = _("Меню")

    markup_organaiser_menu.add(btn1, btn5)
    markup_organaiser_menu.add(btn2, btn4)
    markup_organaiser_menu.add(btn3, btn6)

    return markup_organaiser_menu


async def markup_peoples_menu(telegram_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    count_my_socium = len(await dbs.rings_help.get_my_socium(telegram_id))

    list_intentions_to = await dbs.intentions.get_intentions(statuses=[1, 11, 12, 13], to_id=telegram_id)
    set_intentions_ids_to = set([intention.from_id for intention in list_intentions_to])
    intentions_to_count = len(set_intentions_ids_to)

    list_intentions_from = await dbs.intentions.get_intentions(statuses=[1, 11, 12, 13], from_id=telegram_id)
    set_intentions_ids_from = set([intention.to_id for intention in list_intentions_from])
    intentions_from_count = len(set_intentions_ids_from)

    btn1 = emojize(_("Моя сеть :busts_in_silhouette:{}")).format(count_my_socium)
    btn2 = emojize(f"{intentions_to_count}:busts_in_silhouette: → :bust_in_silhouette:")
    btn3 = _("Расширить сеть")
    btn4 = emojize(_(":link: Помочь"))
    btn5 = emojize(f":bust_in_silhouette: → {intentions_from_count}:busts_in_silhouette:")
    btn6 = _("Меню")

    markup.row(btn1, btn2, btn3)
    markup.add(btn4, btn5, btn6)

    return markup


async def markup_faq_menu():
    markup_faq_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup_faq_menu.add(_("Про бота"), _("Описание меню"), _("Условные обозначения"))
    markup_faq_menu.add(_("Как начать пользоваться"), _("Возможные кейсы"), _("Меню"))

    return markup_faq_menu


async def markup_profile_menu(lang=None):
    user_from_tg = types.User.get_current()
    user_from_db = await dbs.users.get_user(user_from_tg.id)

    status = await get_status_emoji(user_from_db.status)
    markup_profile_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    if lang:
        btn1 = emojize(status) + _("Статус", locale=lang)
        btn2 = emojize(":speech_balloon:") + _("Обо мне", locale=lang)
        btn3 = emojize(":credit_card:") + _("Реквизиты", locale=lang)
        btn4 = emojize(_(":footprints: Выйти из бота", locale=lang))
        btn5 = _('RU→ENG', locale=lang)
        btn6 = _("Меню", locale=lang)

        markup_profile_menu.add(btn1, btn2, btn3)
        markup_profile_menu.add(btn4, btn5, btn6)
    else:
        btn1 = emojize(status) + _("Статус")
        btn2 = emojize(":speech_balloon:") + _("Обо мне")
        btn3 = emojize(":credit_card:") + _("Реквизиты")
        btn4 = emojize(_(":footprints: Выйти из бота"))
        btn5 = _('RU→ENG')
        btn6 = _("Меню")

        markup_profile_menu.add(btn1, btn2, btn3)
        markup_profile_menu.add(btn4, btn5, btn6)

    return markup_profile_menu


async def select_data_status_reply_kb():
    markup_select_data_reply_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    user_from_tg = types.User.get_current()
    user_from_db = await dbs.users.get_user(user_from_tg.id)
    status = user_from_db.status

    btn1 = _("Изменить данные")
    btn2 = _("Изменить статус")
    btn3 = _("Назад")

    if status == 'green':
        markup_select_data_reply_kb.add(btn2, btn3)
    else:
        markup_select_data_reply_kb.add(btn1, btn2, btn3)
    return markup_select_data_reply_kb


async def change_status_reply_kb():
    user_from_tg = types.User.get_current()
    user_from_db = await dbs.users.get_user(user_from_tg.id)
    status = user_from_db.status
    markup_status_reply_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    if status == 'green':
        markup_status_reply_kb.add(emojize(":sos:"), emojize(":high_brightness:"), _("Назад"))
    elif status == 'orange':
        markup_status_reply_kb.add(emojize(":sos:"), emojize(":white_check_mark:"), _("Назад"))
    elif status == 'redorange':
        markup_status_reply_kb.add(_("Вернуться к ") + emojize(":high_brightness:"), _("Назад"))
    elif status == 'redgreen':
        markup_status_reply_kb.add(_("Вернуться к ") + emojize(":white_check_mark:"), _("Назад"))

    return markup_status_reply_kb


async def proof_change_status_reply_kb():
    markup_proof_change_status_reply_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    btn1 = _("Да, изменить")
    btn2 = _("Нет, вернуться назад")

    markup_proof_change_status_reply_kb.add(btn1, btn2)
    return markup_proof_change_status_reply_kb


async def proof_return_orange_reply_kb():
    markup_proof_return_orange_reply_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    btn1 = _("Сохранить")
    btn2 = _("Отмена")

    markup_proof_return_orange_reply_kb.add(btn1, btn2)
    return markup_proof_return_orange_reply_kb


async def final_proof_change_status_reply_kb():
    markup_final_proof_change_status_reply_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    btn1 = _("Сохранить")
    btn2 = _("Отмена")

    markup_final_proof_change_status_reply_kb.add(btn1, btn2)
    return markup_final_proof_change_status_reply_kb


async def log_out_from_bot():
    markup_log_out = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup_log_out.add(_("Да, удалить профиль"), _("Нет, я остаюсь"))

    return markup_log_out


async def start_orange_invitation_kb(user_to):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    status = user_to.status

    intentions_to_count, intentions_to_sum = await get_intentions_count_sum_to(to_id=user_to.tg_id)

    if status == "orange":
        obligations_to_count, obligations_to_sum = await get_all_obligations_count_sum_to(to_id=user_to.tg_id,
                                                                                      user_status="orange",
                                                                                      statuses=[11, 12])
        btn1 = emojize('{}:busts_in_silhouette: → {}'.format(intentions_to_count + obligations_to_count, user_to.name))

    elif "red" in status:
        obligations_to_count, obligations_to_sum = await get_all_obligations_count_sum_to(to_id=user_to.tg_id,
                                                                                      user_status="red",
                                                                                      statuses=[11, 12])
        btn1 = emojize('{}:busts_in_silhouette: → {}'.format(obligations_to_count, user_to.name))

    btn2 = _('Нет')
    btn3 = _('Да')
    btn4 = _('Меню')

    markup.row(btn2, btn3)
    markup.row(btn1, btn4)

    return markup


async def back_kb():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    btn1 = _('Назад')
    markup.row(btn1)

    return markup


async def requisites_menu_kb():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    requisites = await dbs.requisites.get_all_requisites()
    for req in requisites:
        if req.is_default:
            markup.row(req.name + ' (' + _('по умолчанию') + ')')
        else:
            markup.row(req.name)

    btn1 = _('Добавить реквизиты')
    btn2 = _('Назад')
    markup.row(btn1, btn2)

    return markup


async def requisites_add_check_kb():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    btn1 = _('Да')
    btn2 = _('Нет')
    btn3 = _('Да, сделать реквизитами по умолчанию')
    btn4 = _('Отмена')

    markup.row(btn1, btn2)
    markup.row(btn3)
    markup.row(btn4)

    return markup


async def requisites_edit_kb():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    btn1 = _('Редактировать данные')
    btn2 = _('Сделать реквизитами по умолчанию')
    btn3 = _('Удалить')
    btn4 = _('Назад')

    markup.row(btn1, btn2)
    markup.row(btn3, btn4)

    return markup


async def intention_settings_kb():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    btn1 = emojize(_('Отменить :heart:'))
    btn2 = _('Изменить')
    btn3 = emojize(_('В :handshake:'))
    btn4 = _('Назад')
    btn5 = emojize(_('Исполнить :heart:'))
    btn6 = _('Меню')

    markup.row(btn1, btn2, btn3)
    markup.row(btn4, btn5, btn6)

    return markup


async def proof_yes_no_kb():
    markup_proof_yes_no_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    btn1 = _("Да")
    btn2 = _("Нет")

    markup_proof_yes_no_kb.add(btn1, btn2)
    return markup_proof_yes_no_kb


async def proof_obligation_kb():
    markup_proof_obligation_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    btn1 = emojize(_("Да, я исполнил :handshake:"))
    btn2 = _("Назад")

    markup_proof_obligation_kb.add(btn1, btn2)
    return markup_proof_obligation_kb


async def check_intention_for_me():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    btn1 = emojize(_("Попросить :heart: → :handshake:"))
    btn2 = _("Назад")
    btn3 = _("Меню")

    markup.add(btn1, btn2, btn3)
    return markup


async def check_obligation_for_me():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    btn1 = _("Запрос на исполнение")
    # btn2 = emojize(_("Простить :handshake:"))
    btn3 = _("Назад")
    btn4 = _("Меню")

    markup.add(btn1, btn3, btn4)
    return markup


async def markup_edit_profile():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    btn1 = _("Изменить имя")
    btn2 = _("Изменить обо мне")
    btn3 = _("Назад")

    markup.add(btn1, btn2, btn3)
    return markup

