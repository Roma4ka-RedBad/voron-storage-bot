from peewee import SqliteDatabase, Model

database = SqliteDatabase("database.db")


class BaseModel(Model):
    class Meta:
        database = database
