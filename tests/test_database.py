import unittest
from peewee import *
from models import Data

# test_db = SqliteDatabase('wee.db', pragmas={'journal_mode': 'wal'})
test_db = SqliteDatabase('wee.db')


class TestDB(unittest.TestCase):

    def setUp(self):
        test_db.bind([Data], bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables([Data])
        with test_db.atomic():
            Data.create(number=1918, title='Private network NAT',
                        text='',
                        category='', bookmark=False)



    def tearDown(self):
        test_db.drop_tables([Data])
        test_db.close()

    def test_db_is_open(self):
        self.assertFalse(test_db.is_closed())

    def test_tables_exist(self):
        self.assertTrue(Data.table_exists())


    def test_table_not_exist(self):
        result = test_db.connect(reuse_if_open=True)
        self.assertFalse(result)
        # self.assertTrue(result)


    def test_rfc_not_exist(self):
        pass

    def test_write_to_database(self):
        result = Data.select().where(Data.number == 1918).get()
        # result = Data.get(number=1918)
        self.assertTrue(result, msg=f'Query Failed: {result}')

    def test_category_exist(self):
        pass


if __name__ == '__main__':
    unittest.main()
