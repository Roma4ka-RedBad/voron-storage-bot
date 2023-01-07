from logic_objects.config import Config
from json import loads, dumps
from box import Box

from peewee import Model, TextField
from peewee_async import Manager, MySQLDatabase
from playhouse.shortcuts import ReconnectMixin


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    pass


database = ReconnectMySQLDatabase(
    Config.MYSQL.database,
    host=Config.MYSQL.host,
    port=Config.MYSQL.port,
    user=Config.MYSQL.username,
    password=Config.MYSQL.password
)


class MyManager(Manager):
    database = database


class BaseModel(Model):
    @classmethod
    async def execute(cls, query):
        objects = MyManager()
        return await objects.execute(query)

    @classmethod
    async def get(cls, *query, **filters):
        objects = MyManager()
        return await objects.get(cls, *query, **filters)

    @classmethod
    async def get_by_id(cls, pk):
        objects = MyManager()
        return await objects.get(cls, cls._meta.primary_key == pk)

    @classmethod
    async def get_or_create(cls, **kwargs):
        objects = MyManager()
        return await objects.get_or_create(cls, defaults=None, **kwargs)

    @classmethod
    async def get_or_none(cls, *query, **filters):
        objects = MyManager()
        try:
            return await objects.get(cls, *query, **filters)
        except:
            pass

    async def asave(self):
        objects = MyManager()
        await objects.update(self)

    @classmethod
    async def get_and_update(cls, *args, **kwargs):
        objects = MyManager()
        data = await objects.get(cls, *args)
        if data:
            for key, value in kwargs.items():
                setattr(data, key, value)
        await objects.update(data)

    class Meta:
        database = database


class ArrayField(TextField):
    def db_value(self, value):
        return super().db_value(str(value))

    def python_value(self, value):
        return loads(super().python_value(value))


class JSONField(TextField):
    def db_value(self, value):
        return super().db_value(str(dumps(value)))

    def python_value(self, value):
        return Box(loads(super().python_value(value)))
