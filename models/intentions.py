from tortoise import Model, fields


class Intentions(Model):
    """
    Коды первой версии

    0 - отменённое намерение
    1 - созданное намерение
    10 - отменённое обязательство
    11 - созданное обязательство (намерение переведено в обязательство)
    12 - деньги на обязательство отправлены, но не подтверждены получателем
    13 - деньги подтверждены отправка и получение

    110 - архивное созданное обязательство (намерение переведено в обязательство)
    120 - архивное деньги на обязательство отправлены, но не подтверждены получателем
    130 - архивное деньги подтверждены отправка и получение

    """
    intention_id = fields.IntField(pk=True)
    from_id = fields.IntField(null=False)
    to_id = fields.IntField(null=False)
    payment = fields.IntField(null=False)
    currency = fields.TextField(null=True)
    user_status = fields.TextField()
    status = fields.IntField(null=False)
    create_date = fields.DatetimeField(null=True)
    active = fields.BooleanField(null=True)

    class Meta:
        table = "intentions"

    async def create_intention(self, active=None, **kwargs):
        if active is None:
            intention = await self.create(active=1, **kwargs)
        else:
            intention = await self.create(active=active, **kwargs)

        return intention

    async def get_intention_from_id(self, intention_id):
        intention = await self.filter(active=1, intention_id=intention_id).first()
        return intention

    async def get_intentions(self, statuses=None, **kwargs):
        if statuses:
            intentions = await self.filter(active=1, status__in=statuses, **kwargs)
        else:
            intentions = await self.filter(active=1, **kwargs)
        return intentions

    async def get_completed_obligations_to(self, to_id):
        intentions = await self.filter(to_id=to_id, status=13).all()
        return intentions

    async def get_completed_obligations_from(self, from_id):
        intentions = await self.filter(from_id=from_id, status=13).all()
        return intentions

    async def update_intention_status(self, old_status, new_status, active=None):
        intentions = await self.filter(status=old_status).all()

        if active is None:
            await self.filter(status=old_status).update(status=new_status)
        else:
            await self.filter(status=old_status).update(status=new_status, active=active)

        return intentions

    async def update_status_from_id(self, intention_id, **kwargs):
        intention = await self.filter(intention_id=intention_id).update(**kwargs)
        return intention

    async def update_payment_from_id(self, intention_id, **kwargs):
        await self.filter(intention_id=intention_id).update(**kwargs)

    async def update_intention_status_with_tg_id(self, old_status, new_status, to_id=None, from_id=None, user_status=None):
        if user_status:
            if to_id:
                await self.filter(to_id=to_id, status=old_status, user_status=user_status).update(status=new_status)
            elif from_id:
                await self.filter(from_id=from_id, status=old_status, user_status=user_status).update(status=new_status)
        else:
            if to_id:
                await self.filter(to_id=to_id, status=old_status).update(status=new_status)
            elif from_id:
                await self.filter(from_id=from_id, status=old_status).update(status=new_status)

    async def update_active(self, to_id, user_status, active):
        await self.filter(to_id=to_id, user_status=user_status).update(active=active)
