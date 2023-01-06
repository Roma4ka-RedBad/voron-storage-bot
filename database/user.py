from datetime import datetime
from peewee import IntegerField, BigIntegerField, TextField, CharField, ForeignKeyField, DateTimeField

from .base import BaseModel
from .metadata import Metadata


class Users(BaseModel):
    vk_id = BigIntegerField(null=True)
    tg_id = BigIntegerField(null=True)
    nickname = TextField(default="")
    rank = IntegerField(default=0)
    language_code = CharField(max_length=4, default='ru')
    warns = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.now)
    metadata = ForeignKeyField(Metadata, backref='user', default=Metadata.create)
    
    @classmethod
    async def get_by_tg_or_vk(cls, tg_id: int = None, vk_id: int = None):
        data = None
        if vk_id is not None:
            data = await super().get_or_create(vk_id=vk_id)
        elif tg_id is not None:
            data = await super().get_or_create(tg_id=tg_id)
        data[0].__data__['metadata'] = await Metadata.get_by_id(data[0].__data__['metadata'])
            
        return data[0]
