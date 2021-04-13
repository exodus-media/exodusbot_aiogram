from tortoise import Model, fields


class Event(Model):
    event_id = fields.IntField(pk=True)
    from_id = fields.IntField(null=False)
    to_id = fields.IntField(null=False)
    payment = fields.IntField()
    currency = fields.TextField(null=True)
    event_status = fields.TextField()
    send = fields.BooleanField(null=True)

    class Meta:
        table = "events"

    async def create_event(self, **kwargs):
        event = await self.create(**kwargs)
        return event

    async def get_events_from_status(self, event_status, send):
        intentions = await self.filter(event_status=event_status, send=send).all()
        return intentions

    async def update_send_event(self, event_id):
        await self.filter(event_id=event_id).update(send=True)