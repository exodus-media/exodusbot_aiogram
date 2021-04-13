from aiogram import types
from tortoise import Model, fields


class Requisites(Model):
    id = fields.IntField(pk=True)
    tg_id = fields.IntField(null=False)
    name = fields.TextField(null=True)
    value = fields.TextField(null=True)
    is_default = fields.BooleanField(null=True)

    class Meta:
        table = "requisites"

    async def get_requisite_for_user(self, tg_id):
        requisite = await self.filter(tg_id=tg_id, is_default=True).first()
        return requisite

    async def get_requisites_from_id(self, req_id):
        tg_user = types.User.get_current()
        requisites = await self.filter(tg_id=tg_user.id, id=req_id).first()
        return requisites

    async def create_requisite(self, name, value):
        tg_user = types.User.get_current()
        actual_req = await self.filter(tg_id=tg_user.id, is_default=True).first()
        if actual_req is not None:
            req = await self.create(tg_id=tg_user.id, name=name, value=value, is_default=False)
        else:
            req = await self.create(tg_id=tg_user.id, name=name, value=value, is_default=True)
        return req

    async def get_all_requisites(self):
        tg_user = types.User.get_current()
        requisites = await self.filter(tg_id=tg_user.id).all()
        return requisites

    async def get_default_requisites(self):
        tg_user = types.User.get_current()
        event = await self.filter(tg_id=tg_user.id, is_default=True).all()
        return event

    async def set_default_requisite(self, id_):
        await self.filter(is_default=True).update(is_default=False)
        req = await self.filter(id=id_).update(is_default=True)
        return req

    async def delete_requisites_and_set_default(self, req_id):
        tg_user = types.User.get_current()
        req = await self.filter(tg_id=tg_user.id, id=req_id).first()
        if req.is_default:
            await self.filter(tg_id=tg_user.id, id=req_id).delete()
            new_default = await self.filter(tg_id=tg_user.id).first()
            if new_default is not None:
                await self.set_default_requisite(new_default.id)
        else:
            await self.filter(tg_id=tg_user.id, id=req_id).delete()

    async def update_requisites(self, req_id, **kwargs):
        tg_user = types.User.get_current()
        await self.filter(id=req_id, tg_id=tg_user.id).update(**kwargs)
