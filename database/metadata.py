from json import loads
from peewee import IntegerField, TextField

from .base import BaseModel


class ArrayField(TextField):
    def db_value(self, value):
        return super().db_value(str(value))

    def python_value(self, value):
        return loads(super().python_value(value))


class Metadata(BaseModel):
    size_limit = IntegerField(default=512)
    files_count_limit = IntegerField(default=100)
    download_count_limit = IntegerField(default=100)
    ban_commands = ArrayField(default=[])
