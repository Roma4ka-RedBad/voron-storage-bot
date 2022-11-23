from peewee import SqliteDatabase, Model, MySQLDatabase

database = SqliteDatabase("database.db")


class BaseModel(Model):
    class Meta:
        database = database
