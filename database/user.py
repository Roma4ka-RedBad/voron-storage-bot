from datetime import datetime
from peewee import IntegerField, TextField, CharField, ForeignKeyField, DateTimeField

from .base import BaseModel
from .metadata import Metadata


class Users(BaseModel):
    vk_id = IntegerField(null=True)
    tg_id = IntegerField(null=True)
    nickname = TextField(default="")
    rank = IntegerField(default=0)
    language_code = CharField(max_length=4, default='ru')
    warns = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.now)
    metadata = ForeignKeyField(Metadata, backref='user', default=Metadata.create)
    
    @classmethod
    def get_by_tg_or_vk(cls, tg_id: int = None, vk_id: int = None):
        data = None
        if vk_id is not None:
            data = cls.get_or_create(vk_id=vk_id)
        elif tg_id is not None:
            data = cls.get_or_create(tg_id=tg_id)
            
        return data[0]
