from playhouse.sqlite_ext import *

from utils import Config

db = SqliteExtDatabase(Config.DATABASE_PATH, pragmas={'journal_mode': 'wal'})


class BaseModel(Model):
    class Meta:
        database = db


class Data(BaseModel):
    """Base model used for rfc files."""
    number = IntegerField(primary_key=True)
    title = CharField()
    text = CharField()
    category = CharField()
    bookmark = BooleanField(default=False)


class DataIndex(FTS5Model):
    """Virtual Table for Full Text Search of :class: Data."""
    rowid = RowIDField()
    title = SearchField()
    text = SearchField(unindexed=False)
    category = SearchField()

    class Meta:
        database = db
        options = {
            'tokenize': 'porter'}  # FTS5 includes more tokenizer options


def create_tables():
    with db:
        db.create_tables([Data, DataIndex], safe=True)
