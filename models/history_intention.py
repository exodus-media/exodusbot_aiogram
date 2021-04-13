from tortoise import Model, fields
from datetime import datetime


class HistoryIntention(Model):

    intention_id = fields.IntField(pk=True)
    from_id = fields.IntField(null=False)
    to_id = fields.IntField(null=False)
    payment = fields.IntField(null=False)
    currency = fields.TextField(null=False)
    create_date = fields.DatetimeField(null=True)
    from_intention = fields.IntField(null=False)
    user_status = fields.TextField()

    class Meta:
        table = "history_intention"

    async def create_history_intention(self, from_id, to_id, payment, from_intention, user_status, currency="€"):
        intention = await self.create(from_id=from_id,
                                      to_id=to_id,
                                      payment=payment,
                                      create_date=datetime.now(),
                                      from_intention=from_intention,
                                      user_status=user_status,
                                      currency=currency)
        return intention

    async def read_history_intention(self, from_id=None, to_id=None, create_date=None):
        if from_id:
            intentions = await self.filter(from_id=from_id).all()
            return intentions

        elif to_id:
            intentions = await self.filter(to_id=to_id).all()
            return intentions