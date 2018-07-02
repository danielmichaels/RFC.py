from peewee import *

db = SqliteDatabase('test.db', pragmas={'journal_mode': 'wal'})


class BaseModel(Model):
    class Meta:
        database = db


class Data(BaseModel):
    number = IntegerField()
    title = CharField()
    text = CharField()
    category = CharField()
    bookmark = BooleanField()


def create_tables():
    with db:
        db.create_tables(Data, safe=True)
