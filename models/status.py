from aiogram import types
from tortoise import Model, fields


class Statuses(Model):
    status_id = fields.IntField(pk=True)
    telegram_id = fields.IntField(null=False)
    payment = fields.IntField(null=True)
    finish_date = fields.DateField(null=True)
    create_date = fields.DateField(null=True)
    type = fields.TextField(null=False)

    class Meta:
        table = "statuses"

    async def create_pair(self):
        tg_user = types.User.get_current()
        orange_status = await self.create(telegram_id=tg_user.id, type='orange')
        red_status = await self.create(telegram_id=tg_user.id, type='red')
        return orange_status, red_status

    async def get_status(self, telegram_id, type):
        status = await self.filter(telegram_id=telegram_id, type=type).first()
        return status

    async def update_status(self, telegram_id, type, **kwargs):
        await self.filter(telegram_id=telegram_id, type=type).update(**kwargs)
