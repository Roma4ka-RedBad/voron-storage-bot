from peewee import Model, MySQLDatabase
from logic_objects import Config


database = MySQLDatabase(
    Config.MYSQL.database,
    host=Config.MYSQL.host,
    port=Config.MYSQL.port,
    user=Config.MYSQL.username,
    password=Config.MYSQL.password
)


class BaseModel(Model):
    class Meta:
        database = database
