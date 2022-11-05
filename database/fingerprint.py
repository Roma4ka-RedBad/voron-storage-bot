from datetime import datetime
from peewee import IntegerField, TextField, DateTimeField, BooleanField

from .base import BaseModel


class Fingerprints(BaseModel):
    major_v = IntegerField(null=False)
    build_v = IntegerField(null=False)
    revision_v = IntegerField(null=False)
    sha = TextField(null=False)
    is_actual = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now())
