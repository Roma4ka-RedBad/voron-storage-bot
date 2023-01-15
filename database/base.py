from logic_objects.config import Config
from json import loads, dumps
from box import Box

from peewee import TextField
from peewee_aio import Manager
from playhouse.shortcuts import ReconnectMixin


#class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
#    pass


'''database = ReconnectMySQLDatabase(
    Config.MYSQL.database,
    host=Config.MYSQL.host,
    port=Config.MYSQL.port,
    user=Config.MYSQL.username,
    password=Config.MYSQL.password
)'''
database = Manager("aiosqlite:///database.db")


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
