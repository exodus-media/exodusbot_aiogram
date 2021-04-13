from datetime import date

from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize

from models.db_service import DBService
from loader import _

dbs = DBService()


async def get_status_emoji(text):
    if text == "green":
        status = emojize(":white_check_mark:")
    elif text == "orange":
        status = emojize(":high_brightness:")
    elif 'red' in text:
        status = emojize(":sos:")
    else:
        status = ""
    return status


# проверка на то, что строка - это число и с плавающей точкой тоже
async def is_digit(string):
    if string.isdigit():
        if int(string) > 0:
            if int(string) == abs(int(string)):
                return True
        else:
            return False
    else:
        try:
            if float(string):
                if float(string) == abs(float(string)):
                    return True
        except ValueError:
            return False


async def make_hash(text):
    hash = text.encode().hex()
    return hash


async def ref_info(text):
    bytes_object = bytes.fromhex(text)
    text = bytes_object.decode("ASCII")
    text = text.split('+')
    return text


async def create_link(botname, from_id, to_id):
    ref = '{}+{}'.format(from_id, to_id)
    hash = await make_hash(ref)
    link = f"https://t.me/{botname}?start={hash}"
    return link


async def get_intentions_count_sum_to(to_id, user_status="orange"):
    intentions_to = await dbs.intentions.get_intentions(to_id=to_id, user_status=user_status, status=1)

    sum = 0
    count = 0
    for intention in intentions_to:
        count += 1
        sum += intention.payment

    return count, sum


async def get_intentions_count_sum_from(from_id):
    intentions_from = await dbs.intentions.get_intentions(from_id=from_id, status=1)

    sum = 0
    count = 0
    for intention in intentions_from:
        count += 1
        sum += intention.payment

    return count, sum


async def get_all_obligations_count_sum_to(to_id, statuses, user_status=None):
    if user_status:
        obligations_from = await dbs.intentions.get_intentions(statuses=statuses, to_id=to_id, user_status=user_status)
    else:
        obligations_from = await dbs.intentions.get_intentions(statuses=statuses, to_id=to_id)

    sum = 0
    count = 0
    for obligation in obligations_from:
        count += 1
        sum += obligation.payment

    return count, sum


async def get_all_obligations_count_sum_from(from_id, statuses):
    obligations_from = await dbs.intentions.get_intentions(statuses=statuses, from_id=from_id)

    sum = 0
    count = 0
    for obligation in obligations_from:
        count += 1
        sum += obligation.payment

    return count, sum


async def get_all_obligations_completed_from(from_id):
    obligations_from = await dbs.history_intention.read_history_intention(from_id=from_id)

    sum = 0
    count = 0
    for obligation in obligations_from:
        count += 1
        sum += obligation.payment

    return count, sum


async def get_all_obligations_completed_to(to_id):
    obligations_from = await dbs.history_intention.read_history_intention(to_id=to_id)

    sum = 0
    count = 0
    for obligation in obligations_from:
        count += 1
        sum += obligation.payment

    return count, sum


async def get_all_info_text_user(bot_username, telegram_id):
    user = await dbs.users.get_user(telegram_id)
    status = await get_status_emoji(user.status)
    link = await create_link(bot_username, telegram_id, telegram_id)

    text = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>  {status}\n'

    if user.status == "green":
        statuses = [1, 11, 12]

        intentions_from = await dbs.intentions.get_intentions(statuses=statuses, from_id=telegram_id)

        if user.link:
            text += _("Инфо ") + emojize(f":speech_balloon: : {user.link}\n")

        text += emojize(f"\n:bust_in_silhouette:→{len(intentions_from)}:busts_in_silhouette:")

    elif user.status == "orange":
        intentions_to_count, intentions_to_sum = await get_intentions_count_sum_to(to_id=telegram_id)
        obligations_to_count, obligations_to_sum = await get_all_obligations_count_sum_to(to_id=telegram_id,
                                                                                          user_status="orange",
                                                                                          statuses=[11, 12])
        obligations_13_to_count, obligations_13_to_sum = await get_all_obligations_count_sum_to(to_id=telegram_id,
                                                                                                user_status="orange",
                                                                                                statuses=[13])
        sum_to = obligations_to_sum + obligations_13_to_sum
        count_to = intentions_to_count + obligations_to_count + obligations_13_to_count

        intentions_from_count, intentions_from_sum = await get_intentions_count_sum_from(from_id=telegram_id)
        obligations_from_count, obligations_from_sum = await get_all_obligations_count_sum_from(from_id=telegram_id,
                                                                                                statuses=[11, 12])
        obligations_13_from_count, obligations_13_from_sum = await get_all_obligations_count_sum_from(
                                                                                                from_id=telegram_id,
                                                                                                statuses=[13])
        count_from = intentions_from_count + obligations_from_count + obligations_13_from_count

        user_from_statuses = await dbs.statuses.get_status(telegram_id=telegram_id, type='orange')
        payment = user_from_statuses.payment
        payment_to = (payment - sum_to) if payment > sum_to else 0

        text += _("Ссылка для помощи ") + emojize(":link: : ") + '<a href="{}">'.format(link) + _("Помочь") + '</a>\n'
        if user.link:
            text += _("Инфо ") + emojize(f":speech_balloon: : {user.link}\n")

        requisite = await dbs.requisites.get_requisite_for_user(telegram_id)
        if requisite:
            req_name = requisite.name + " " + requisite.value
            text += _("Детали ") + emojize(":credit_card: : {}").format(req_name) + "\n\n"
        else:
            text += "\n"

        text += emojize(f"{count_to}:busts_in_silhouette:→:bust_in_silhouette:"
                        f"({intentions_to_sum}:heart: / {payment_to}:pray:)\n")
        text += emojize(f":bust_in_silhouette:→{count_from}:busts_in_silhouette:"
                        f"({intentions_from_sum}:heart: / {obligations_from_sum}:handshake: / {obligations_13_from_sum}👍)")

    else:
        user_from_statuses = await dbs.statuses.get_status(telegram_id, type='red')
        payment = user_from_statuses.payment
        finish_date = user_from_statuses.finish_date
        days_left = (finish_date - date.today()).days

        obligations_to = await dbs.intentions.get_intentions(statuses=[11, 12, 13], to_id=telegram_id,
                                                             user_status="red")
        obligations_to_sum = 0
        for obligation in obligations_to:
            obligations_to_sum += obligation.payment

        payment_to = (payment - obligations_to_sum) if payment > obligations_to_sum else 0

        text += _("Ссылка для помощи ") + emojize(":link: :") + '<a href="{}">'.format(link) + _("Помочь") + '</a>\n'
        if user.link:
            text += _("Инфо ") + emojize(f":speech_balloon: : {user.link}\n")

        requisite = await dbs.requisites.get_requisite_for_user(telegram_id)
        if requisite:
            req_name = requisite.name + " " + requisite.value
            text += _("Детали ") + emojize(":credit_card: :{}").format(req_name) + "\n\n"
        else:
            text += "\n\n"

        text += emojize(
            f"{len(obligations_to)}:busts_in_silhouette:→:bust_in_silhouette:({payment_to}:pray: / {days_left}") + _(
            "дней)")

    return text


async def get_info_text_user_for_invite(telegram_id, bot_username, for_me=None):
    user = await dbs.users.get_user(telegram_id)
    status_emoji = await get_status_emoji(user.status)

    if for_me:
        text = _("Вы {}\n").format(status_emoji)
    else:
        text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'
        text = f"{text_link_user} {status_emoji}\n"
    link = await create_link(bot_username, telegram_id, telegram_id)

    if user.status == "orange":
        intentions_to_count, intentions_to_sum = await get_intentions_count_sum_to(to_id=telegram_id)
        obligations_to_count, obligations_to_sum = await get_all_obligations_count_sum_to(to_id=telegram_id,
                                                                                          user_status="orange",
                                                                                          statuses=[11, 12])
        obligations_13_to_count, obligations_13_to_sum = await get_all_obligations_count_sum_to(to_id=telegram_id,
                                                                                                user_status="orange",
                                                                                                statuses=[13])
        sum_to = obligations_to_sum + obligations_13_to_sum

        user_from_statuses = await dbs.statuses.get_status(telegram_id=telegram_id, type='orange')
        payment = user_from_statuses.payment
        payment_to = (payment - sum_to) if payment > sum_to else 0

        text += emojize(f"({intentions_to_sum}:heart: / {payment_to}:pray:) :link:") + '<a href="{}">'.format(link) + \
                _("Помочь") + '</a>\n'

    elif 'red' in user.status:
        user_from_statuses = await dbs.statuses.get_status(telegram_id, type='red')
        payment = user_from_statuses.payment
        finish_date = user_from_statuses.finish_date
        days_left = (finish_date - date.today()).days

        obligations_to = await dbs.intentions.get_intentions(statuses=[11, 12, 13], to_id=telegram_id,
                                                             user_status="red")
        obligations_to_sum = 0
        for obligation in obligations_to:
            obligations_to_sum += obligation.payment

        payment_to = (payment - obligations_to_sum) if payment > obligations_to_sum else 0

        text += emojize(f"({payment_to}:pray: / {days_left}") + emojize(_("дней) :link:")) + \
                '<a href="{}">'.format(link) + _("Помочь") + '</a>\n'
    return text


async def get_info_text_user_for_circle(telegram_id, bot_username):
    user = await dbs.users.get_user(telegram_id)
    link = await create_link(bot_username, telegram_id, telegram_id)
    status_emoji = await get_status_emoji(user.status)
    text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

    text = f"{text_link_user} {status_emoji}\n"

    if user.status == "orange":
        intentions_to_count, intentions_to_sum = await get_intentions_count_sum_to(to_id=telegram_id)
        obligations_to_count, obligations_to_sum = await get_all_obligations_count_sum_to(to_id=telegram_id,
                                                                                          user_status="orange",
                                                                                          statuses=[11, 12])
        obligations_13_to_count, obligations_13_to_sum = await get_all_obligations_count_sum_to(to_id=telegram_id,
                                                                                                user_status="orange",
                                                                                                statuses=[13])
        sum_to = obligations_to_sum + obligations_13_to_sum

        user_from_statuses = await dbs.statuses.get_status(telegram_id=telegram_id, type='orange')
        payment = user_from_statuses.payment
        payment_to = (payment - sum_to) if payment > sum_to else 0

        text += emojize(f" ({intentions_to_sum}:heart:/{payment_to} :pray:) :link:") + '<a href="{}">'.format(link) + \
                _("Помочь") + '</a>\n'

    elif 'red' in user.status:
        user_from_statuses = await dbs.statuses.get_status(telegram_id, type='red')
        payment = user_from_statuses.payment
        finish_date = user_from_statuses.finish_date
        days_left = (finish_date - date.today()).days

        obligations_to = await dbs.intentions.get_intentions(statuses=[11, 12, 13], to_id=telegram_id,
                                                             user_status="red")
        obligations_to_sum = 0
        for obligation in obligations_to:
            obligations_to_sum += obligation.payment

        payment_to = (payment - obligations_to_sum) if payment > obligations_to_sum else 0

        text += emojize(f" ({payment_to}:pray:/{days_left}") + emojize(_("дней) :link:")) + '<a href="{}">'.format(link) + _("Помочь") + '</a>\n'
    return text


async def get_short_info_text_user(telegram_id):
    user = await dbs.users.get_user(telegram_id)
    status = await get_status_emoji(user.status)
    text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

    text = f"{text_link_user} {status}\n"
    return text


async def get_list_invite_for_user(to_id):
    user = await dbs.users.get_user(to_id)
    status = user.status

    text = ''

    if "orange" == status:
        intentions_to_count, intentions_to_sum = await get_intentions_count_sum_to(to_id=to_id)
        obligations_to_count, obligations_to_sum = await get_all_obligations_count_sum_to(to_id=to_id,
                                                                                          user_status="orange",
                                                                                          statuses=[11, 12])

        count_to = intentions_to_count + obligations_to_count

        text = emojize(_('Участнику {} помогают {} :busts_in_silhouette:\n\n').format(user.name, count_to))

        list_intentions = await dbs.intentions.get_intentions(statuses=[1, 11, 12], to_id=to_id)
        for intention in list_intentions:
            text += await get_short_info_text_user(intention.from_id)
    elif "red" in status:
        obligations_to_count, obligations_to_sum = await get_all_obligations_count_sum_to(to_id=to_id,
                                                                                          user_status="red",
                                                                                          statuses=[11, 12])
        text = emojize(_('Участнику {} помогают {} :busts_in_silhouette:\n\n').format(user.name, obligations_to_count))

        list_intentions = await dbs.intentions.get_intentions(statuses=[11, 12], to_id=to_id)
        for intention in list_intentions:
            text += await get_short_info_text_user(intention.from_id)

    return text


async def create_dict_intention(statuses, from_id=None, to_id=None):
    dict_ = {}
    count = 1
    if from_id:
        intentions = await dbs.intentions.get_intentions(statuses=statuses, from_id=from_id)
        for intention in intentions:
            dict_[count] = intention.intention_id
            count += 1

    if to_id:
        intentions = await dbs.intentions.get_intentions(statuses=statuses, to_id=to_id)
        for intention in intentions:
            dict_[count] = intention.intention_id
            count += 1

    return dict_


async def get_sum_int_obl(telegram_id):
    user = await dbs.users.get_user(telegram_id)

    text = ""

    if user.status == "orange":
        intentions_to_count, intentions_to_sum = await get_intentions_count_sum_to(to_id=telegram_id)
        obligations_to_count, obligations_to_sum = await get_all_obligations_count_sum_to(to_id=telegram_id,
                                                                                          user_status="orange",
                                                                                          statuses=[11, 12])
        obligations_13_to_count, obligations_13_to_sum = await get_all_obligations_count_sum_to(to_id=telegram_id,
                                                                                                user_status="orange",
                                                                                                statuses=[13])
        sum_to = obligations_to_sum + obligations_13_to_sum

        user_from_statuses = await dbs.statuses.get_status(telegram_id=telegram_id, type='orange')
        payment = user_from_statuses.payment
        payment_to = (payment - sum_to) if payment > sum_to else 0

        text += emojize(f"({intentions_to_sum}:heart:/{payment_to} :pray:)")

    elif 'red' in user.status:
        user_from_statuses = await dbs.statuses.get_status(telegram_id, type='red')
        payment = user_from_statuses.payment
        finish_date = user_from_statuses.finish_date
        days_left = (finish_date - date.today()).days

        obligations_to = await dbs.intentions.get_intentions(statuses=[11, 12, 13], to_id=telegram_id,
                                                             user_status="red")
        obligations_to_sum = 0
        for obligation in obligations_to:
            obligations_to_sum += obligation.payment

        payment_to = (payment - obligations_to_sum) if payment > obligations_to_sum else 0

        text += emojize(f"({payment_to}:pray:/{days_left}") + emojize(_("дней)"))
    return text


async def create_list_intention(dict_intention, from_id=None, to_id=None):
    text = ""

    if from_id:
        for i in dict_intention:
            intention = await dbs.intentions.get_intention_from_id(intention_id=dict_intention[i])
            user = await dbs.users.get_user(intention.to_id)
            text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

            status = await get_status_emoji(user.status)
            int_and_obl = await get_sum_int_obl(intention.to_id)
            if intention.status == 1:
                text += emojize(f"{i}. {text_link_user} {status} {int_and_obl} {intention.payment} :heart:\n")
            elif intention.status == 11:
                text += emojize(f"{i}. {text_link_user} {status} {int_and_obl} {intention.payment} :handshake:\n")

    elif to_id:
        for i in dict_intention:
            intention = await dbs.intentions.get_intention_from_id(intention_id=dict_intention[i])
            user = await dbs.users.get_user(intention.from_id)
            text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

            status = await get_status_emoji(user.status)
            int_and_obl = await get_sum_int_obl(intention.from_id)
            if intention.status == 1:
                text += emojize(f"{i}. {text_link_user} {status} {int_and_obl} {intention.payment} :heart:\n")
            elif intention.status == 11:
                text += emojize(f"{i}. {text_link_user} {status} {int_and_obl} {intention.payment} :handshake:\n")

    return text


async def text_status_to_green():
    text = emojize(_("""
Вы собираетесь сменить статус на :white_check_mark:
Пожалуйста подтвердите смену статуса:

Если ваш статус был :high_brightness: или :sos:, все :heart: участников в Вашу пользу будут автоматически удалены.

Все 🤝 участников в Вашу пользу останутся в силе. Посмотреть все 🤝 можно в разделе главного меню "Органайзер"
    """))
    return text


async def text_status_to_orange():
    text = emojize(_("""
Вы собираетесь сменить статус на :high_brightness:
Пожалуйста подтвердите смену статуса
    """))
    return text


async def text_input_sum_orange(sum):
    text = emojize(_("""Пожалуйста проверьте введенные данные:
Статус: :high_brightness:
Период: Ежемесячно
Необходимая сумма: {}€

Опубликовать эти данные?
Все пользователи, которые связаны с вами внутри Эксодус бота, получат уведомление.""")).format(sum)
    return text


async def text_return_to_orange(sum):
    text = emojize(_("""
Ваш статус возвращается на :high_brightness:
Пожалуйста проверьте введенные данные:
    
Статус: :high_brightness:
Период: Ежемесячно
Необходимая сумма: {}€

Опубликовать эти данные?
Все пользователи, которые связаны с вами внутри Эксодус бота, получат уведомление.
    """)).format(sum)
    return text


async def text_for_status_menu(telegram_id):
    user = await dbs.users.get_user(telegram_id)
    status = user.status
    emoji_status = await get_status_emoji(status)
    if status == 'green':
        text = emojize(_("""Ваш статус: :white_check_mark:
Список участников, с которыми вы связаны, можно посмотреть в разделе главного меню 'Участники'"""))
        return text
    elif "red" in status:
        status_from_db = await dbs.statuses.get_status(telegram_id, "red")

        finish_date = status_from_db.finish_date
        days_stay = (finish_date - date.today()).days
        text = emoji_status + emojize(":moneybag: {}€".format(status_from_db.payment)) + _(
            ", осталось {} дней".format(days_stay))
        return text
    elif status == 'orange':
        status_from_db = await dbs.statuses.get_status(telegram_id, "orange")
        text = emoji_status + emojize(":moneybag: {}€".format(status_from_db.payment)) + _(", ежемесячно")
        return text


async def text_intention_to(intention_id):
    intention = await dbs.intentions.get_intention_from_id(intention_id)
    user = await dbs.users.get_user(intention.from_id)
    status = await get_status_emoji(user.status)
    text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

    date = intention.create_date.date()

    text = emojize("{}\n{} → :heart: {} {}").format(date, text_link_user, status, intention.payment, intention.currency)
    return text


async def text_obligation_to(obligation_id):
    obligation = await dbs.intentions.get_intention_from_id(obligation_id)
    user = await dbs.users.get_user(obligation.from_id)
    status = await get_status_emoji(user.status)
    text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

    text = emojize("{} {} → :handshake: {} {}").format(text_link_user, status, obligation.payment,
                                                       obligation.currency)
    return text


async def text_need_intention_to_obligation():
    text = emojize(_("Отправлен запрос на :heart:→:handshake:"))
    return text


async def text_need_intention_to_sponsor(intention_id):
    intention = await dbs.intentions.get_intention_from_id(intention_id)
    user = await dbs.users.get_user(intention.to_id)
    status = await get_status_emoji(user.status)

    text = emojize(_("Просьба :heart:→:handshake: для {} {} на сумму {} {}")).format(user.name, status,
                                                                                     intention.payment,
                                                                                     intention.currency)
    return text


async def text_need_obligation(obligation_id):
    obligation = await dbs.intentions.get_intention_from_id(obligation_id)
    user = await dbs.users.get_user(obligation.from_id)
    status = await get_status_emoji(user.status)
    text = emojize(_("Участнику {} {} направлено уведомление с "
                     "просьбой исполнить 🤝 на сумму {} {}")).format(user.name,
                                                                     status,
                                                                     obligation.payment,
                                                                     obligation.currency)
    return text


async def text_need_obligation_to_sponsor(obligation_id):
    obligation = await dbs.intentions.get_intention_from_id(obligation_id)
    user = await dbs.users.get_user(obligation.to_id)
    status = await get_status_emoji(user.status)
    requisite = await dbs.requisites.get_requisite_for_user(obligation.to_id)
    if requisite:
        req_name = requisite.name + " " + requisite.value
    else:
        req_name = _("спросить лично")

    text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'
    text = emojize(_("Ваше обязательство 🤝 на сумму {} {} в пользу {} {}\n\n"
                     ":credit_card:Реквизиты для помощи:\n{}")).format(obligation.payment,
                                                                       obligation.currency,
                                                                       text_link_user,
                                                                       status,
                                                                       req_name)
    return text


async def text_forgive_obligation_to(obligation_id):
    obligation = await dbs.intentions.get_intention_from_id(obligation_id)
    user = await dbs.users.get_user(obligation.to_id)
    status = await get_status_emoji(user.status)
    text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

    text = emojize(_("🤝 перед участником {} {} на сумму {} {} прощено")).format(text_link_user,
                                                                                 status,
                                                                                 obligation.payment,
                                                                                 obligation.currency)
    return text


async def text_proof_forgive_obligation_from(obligation_id):
    obligation = await dbs.intentions.get_intention_from_id(obligation_id)
    user = await dbs.users.get_user(obligation.from_id)
    status = await get_status_emoji(user.status)
    text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

    text = emojize(_("Вы хотите простить 🤝 участнику {} {} на {} {}?")).format(text_link_user,
                                                                                status,
                                                                                obligation.payment,
                                                                                obligation.currency)
    return text


async def text_final_forgive_obligation_from(obligation_id):
    obligation = await dbs.intentions.get_intention_from_id(obligation_id)
    user = await dbs.users.get_user(obligation.from_id)
    status = await get_status_emoji(user.status)
    text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

    text = emojize(_("Вы простили 🤝 участника {} {} на {} {}")).format(text_link_user,
                                                                        status,
                                                                        obligation.payment,
                                                                        obligation.currency)
    return text


async def text_sum_digit():
    text = _('Ввод должен быть только в виде цифр и больше 0')
    return text


async def check_number_dict():
    text = _('Такой записи не существует. Попробуйте ввести корректный номер')
    return text


async def is_it_requisites(value, requisites):
    for i in requisites:
        if i.name in value:
            return i
    return False


async def show_help_to_me(telegram_id, bot_username, state: FSMContext):

    list_intentions = await dbs.intentions.get_intentions(statuses=[1, 11, 12, 13], to_id=telegram_id)
    list_intentions_ids = set([intention.from_id for intention in list_intentions])

    string_name = ''
    dict_socium = {}
    count = 0
    for id_help in list_intentions_ids:
        count += 1
        dict_socium[count] = id_help
        text_user = await get_info_text_user_for_circle(id_help, bot_username)
        string_name += f"{count}. {text_user}\n"

    await state.update_data(dict_socium=dict_socium)

    return string_name


async def show_help_from_me(telegram_id, bot_username, state: FSMContext):

    list_intentions = await dbs.intentions.get_intentions(statuses=[1, 11, 12, 13], from_id=telegram_id)
    set_intentions_ids = set([intention.to_id for intention in list_intentions])

    string_name = ''
    dict_socium = {}
    count = 0
    for id_help in set_intentions_ids:
        count += 1
        dict_socium[count] = id_help
        text_user = await get_info_text_user_for_circle(id_help, bot_username)
        string_name += f"{count}. {text_user}\n"

    await state.update_data(dict_socium=dict_socium)

    return string_name


async def send_notify_for_auto_end_red(user_id):
    user = await dbs.users.get_user(user_id)
    text_link_user = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'

    text_for_other_people = emojize(_("{} завершил сбор помощи в :sos: статусе\n" \
                                      "Незавершенные транзакции помощи для этого сбора перемещены в архив :hourglass: "
                                      "и должны быть исполнены/подтверждены.")).format(text_link_user)

    return text_for_other_people


async def text_input_number_people():
    result_text = _('\nВведите номер, указанный перед именем Участника в списке, чтобы посмотреть о нем подробную информацию')
    return result_text


async def text_faq():
    result_text = _("""Узнать подробнее о системе Эксодус можно, присоединившись к нашему каналу https://t.me/Exodus_canal_1

Вы можете сообщить про неясности или ошибки, возникающие в ходе освоения и доработки бота: https://t.me/Exodus_canal_1/4

Использование бота позволяет формировать список участников взаимной помощи, что является необходимым условием возникновения децентрализованной сети доверия.

Выберите пояснение к использованию бота.""")

    return result_text