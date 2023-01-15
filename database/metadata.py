from peewee import IntegerField
from .base import database, ArrayField


class Metadata(database.Model):
    size_limit = IntegerField(default=512)
    files_count_limit = IntegerField(default=100)
    download_count_limit = IntegerField(default=100)
    ban_commands = ArrayField(default=[])
