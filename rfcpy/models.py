"""Data models for use in the RFC.py application.

Sqlite engine used as a lightweight and extensible storage with support for
Full Text Search (Sqlite FTS5). SQL managed by the PeeWee ORM.

All credit: <https://github.com/coleifer/peewee>
"""

from playhouse.sqlite_ext import *

from rfcpy.config import Config

db = SqliteExtDatabase(Config.DATABASE_PATH, pragmas={"journal_mode": "wal"})


class BaseModel(Model):
    """Base model that all classes inherit from."""

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
    text = SearchField(unindexed=True)  # False returns too many hits in text
    category = SearchField()

    class Meta:
        database = db
        options = {"tokenize": "porter"}  # FTS5 includes more tokenizer options
