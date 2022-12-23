from json import loads, dumps
from box import Box
from peewee import Model, SqliteDatabase, TextField
from logic_objects import Config

'''database = MySQLDatabase(
    Config.MYSQL.database,
    host=Config.MYSQL.host,
    port=Config.MYSQL.port,
    user=Config.MYSQL.username,
    password=Config.MYSQL.password
)'''
database = SqliteDatabase('database.db')


class BaseModel(Model):
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
