from datetime import datetime
from peewee import IntegerField, TextField, DateTimeField

from .base import BaseModel


class User(BaseModel):
    vk_id = IntegerField(null=True)
    tg_id = IntegerField(null=True)
    nickname = TextField(null=True)
    rank = IntegerField(default=0)
    size_multiplier = IntegerField(default=1)
    warns = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.now())
