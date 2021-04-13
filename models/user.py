from aiogram import types
from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    tg_id = fields.IntField(unique=True, null=False)
    name = fields.TextField()
    username = fields.TextField(null=True)
    language = fields.TextField(null=False)
    status = fields.TextField(null=False)
    link = fields.TextField(null=True)

    class Meta:
        table = "users"

    async def get_user(self, telegram_id):
        user = await self.filter(tg_id=telegram_id).first()
        return user

    async def get_all_users(self):
        users = await self.all()
        return users

    async def create_user(self, language):
        user = types.User.get_current()
        new_user = await self.create(tg_id=user.id,
                                     username=user.username,
                                     name=user.full_name,
                                     status='green',
                                     language=language)
        return new_user

    async def set_language(self, language):
        telegram_id = types.User.get_current().id
        user = await self.get_user(telegram_id)
        await user.filter(tg_id=telegram_id).update(language=language)

    async def update_user(self, telegram_id, **kwargs):
        await self.filter(tg_id=telegram_id).update(**kwargs)

    async def delete_user(self, telegram_id):
        await self.filter(tg_id=telegram_id).delete()
