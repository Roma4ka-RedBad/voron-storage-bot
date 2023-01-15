from datetime import datetime
from peewee import IntegerField, BigIntegerField, TextField, CharField, ForeignKeyField, DateTimeField

from .base import database
from .metadata import Metadata


class Users(database.Model):
    vk_id = BigIntegerField(null=True)
    tg_id = BigIntegerField(null=True)
    nickname = TextField(default="")
    rank = IntegerField(default=0)
    language_code = CharField(max_length=4, default='ru')
    warns = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.now)
    metadata = ForeignKeyField(Metadata, backref='user')

    @classmethod
    async def get_by_tg_or_vk(cls, tg_id: int = None, vk_id: int = None):
        data = None
        if vk_id is not None:
            data = await cls.get_or_none(vk_id=vk_id)
        elif tg_id is not None:
            data = await cls.get_or_none(tg_id=tg_id)

        if not data:
            metadata = await Metadata.create()
            data = await cls.create(tg_id=tg_id, vk_id=vk_id, metadata=metadata.id)

        data.__data__["metadata"] = await data.metadata

        return data
