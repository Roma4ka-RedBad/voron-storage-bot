from peewee import IntegerField
from .base import BaseModel, ArrayField


class Metadata(BaseModel):
    size_limit = IntegerField(default=512)
    files_count_limit = IntegerField(default=100)
    download_count_limit = IntegerField(default=100)
    ban_commands = ArrayField(default=[])
