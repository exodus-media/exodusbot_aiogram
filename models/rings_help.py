from aiogram import types
from tortoise import Model, fields


class RingsHelp(Model):
    id = fields.IntField(pk=True)
    needy_id = fields.IntField(unique=True)
    help_array = fields.JSONField(null=True)

    class Meta:
        table = "rings_help"

    async def create_rings_help(self, help_array=None):
        if help_array is None:
            help_array = []
        tg_user = types.User.get_current()
        pair = await self.get_or_create(needy_id=tg_user.id, help_array=help_array)
        return pair

    async def read_rings_help(self, needy_id):
        users_id = await self.filter(needy_id=needy_id).first()
        return users_id

    async def read_rings_help_in_help_array(self, telegram_id):
        list_ = await self.filter(help_array__contains=telegram_id).all()
        return list_

    async def update_rings_help_array(self, needy_id, help_array):
        await self.filter(needy_id=needy_id).update(help_array=help_array)

    async def add_to_help_array(self, needy_id, help_id):
        temp_d = await self.filter(needy_id=needy_id).first()
        new_help_array = set(temp_d.help_array)
        if new_help_array:
            new_help_array.add(help_id)
        else:
            new_help_array = [help_id]
        await self.filter(needy_id=needy_id).update(help_array=list(new_help_array))

    async def delete_from_help_array(self, needy_id, delete_id):
        """
        :param needy_id: в пользу кого была помощь
        :param delete_id: кто перестал помогать и вышел из круга
        :return:
        """
        try:
            rings_help = set((await self.read_rings_help(needy_id)).help_array)
        except:
            rings_help = set()

        rings_help.discard(delete_id)
        await self.update_rings_help_array(needy_id, list(rings_help))

    # создаем список с моей сетью
    async def get_my_socium(self, telegram_id):
        # создаем список с теми, кто помогает мне
        try:
            list_needy_id = set((await self.read_rings_help(telegram_id)).help_array)
        except:
            list_needy_id = set()

        # добавляем в список тех, кому помогаю я
        list_send_notify = await self.read_rings_help_in_help_array(telegram_id)
        for row in list_send_notify:
            list_needy_id.add(row.needy_id)

        # добавляем в список людей, которые вместе со мной помогат кому то
        for row in list_send_notify:
            for id_ in row.help_array:
                list_needy_id.add(id_)
                # люди, которым помогает кто-то из тех, с кем мы вместе помогаем кому то
                list_other_needy = await self.read_rings_help_in_help_array(id_)
                for id_other in list_other_needy:
                    list_needy_id.add(id_other.needy_id)

        # удаляем себя из списка
        list_needy_id.discard(telegram_id)

        return list_needy_id

    # создаем список с моей маленькой сетью
    async def get_my_socium_small(self, telegram_id):
        # создаем список с теми, кто помогает мне
        try:
            list_needy_id = set((await self.read_rings_help(telegram_id)).help_array)
        except:
            list_needy_id = set()

        # добавляем в список тех, кому помогаю я
        list_send_notify = await self.read_rings_help_in_help_array(telegram_id)
        for row in list_send_notify:
            list_needy_id.add(row.needy_id)

        # удаляем себя из списка
        list_needy_id.discard(telegram_id)

        return list_needy_id
