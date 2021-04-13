import asyncio
from datetime import datetime

from aiogram.utils.emoji import emojize
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from models.db_service import DBService
from loader import _

# Помощь в составлении правила cron
# https://crontab.guru
from utils.util_bot import send_message

dbs = DBService()


async def first_day_month():
    intentions = await dbs.intentions.update_intention_status(1, 0, active=False)
    for intention in intentions:
        await dbs.rings_help.delete_from_help_array(intention.to_id, intention.from_id)

    await dbs.intentions.update_intention_status(11, 110)
    await dbs.intentions.update_intention_status(12, 120)
    await dbs.intentions.update_intention_status(13, 0)

    events = await dbs.events.get_events_from_status(event_status="future_event", send=False)
    for event in events:
        await dbs.events.update_send_event(event.event_id)
        """
        Проверяем в каком статусе находится получатель, 
        чтобы при красном статусе ему не висело намерение для его желтого статуса
        """
        user_to = await dbs.users.get_user(event.to_id)
        if user_to.status == "orange":
            await dbs.intentions.create_intention(from_id=event.from_id,
                                                  to_id=event.to_id,
                                                  payment=event.payment,
                                                  currency=event.currency,
                                                  create_date=datetime.now(),
                                                  user_status="orange",
                                                  status=1)
        elif 'red' in user_to.status:
            await dbs.intentions.create_intention(active=0,
                                                  from_id=event.from_id,
                                                  to_id=event.to_id,
                                                  payment=event.payment,
                                                  currency=event.currency,
                                                  create_date=datetime.now(),
                                                  user_status="orange",
                                                  status=1)

    return


async def for_five_day():
    text = emojize(_("Завершается месяц.\n\nПроверьте, есть ли у вас транзакции, которые необходимо завершить до конца "
                     "месяца.\n\nВсе незавершенные транзакции с обязательствами 🤝 1-го числа уйдут в архив "
                     "долгов/неподтвержденных обязательств :hourglass: в органайзере 🗓, где вы сможете завершить "
                     "их.\n\nНамерения :heart:, которые не подтверждены, будут отменены и вы выйдете из этого круга "
                     "помощи.\nИсполненные обязательства :+1: в следующем месяце продлятся как намерение :heart: "
                     "продолжить помощь. Вы сможете их подтвердить, скорректировать или отменить."))

    all_users = await dbs.users.get_all_users()
    for user in all_users:
        await send_message(user.tg_id, text)
        await asyncio.sleep(.05)


sched = AsyncIOScheduler()

# первое число каждаго месяца каждого года в 00 часов в 00 минут
sched.add_job(first_day_month, CronTrigger.from_crontab('0 0 1 * *'))

sched.add_job(for_five_day, CronTrigger.from_crontab('0 0 25 * *'))


async def scheduler_init():
    sched.start()


