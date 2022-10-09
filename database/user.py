from datetime import datetime
from peewee import IntegerField, TextField, DateTimeField, CharField

from .base import BaseModel


class Users(BaseModel):
    vk_id = IntegerField(null=True)
    tg_id = IntegerField(null=True)
    nickname = TextField(default="")
    rank = IntegerField(default=0)
    language_code = CharField(max_length=4, default='ru')
    warns = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.now())
