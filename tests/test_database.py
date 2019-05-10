import unittest

from playhouse.sqlite_ext import SqliteExtDatabase

from rfcpy.models import Data, DataIndex

test_db = SqliteExtDatabase(":memory:")


class TestDB(unittest.TestCase):
    """Test database connections."""

    def setUp(self):
        """Setup the database and create one entry, including the sqlite3
        full-text search. Database is peewee ORM."""
        test_db.bind([Data, DataIndex], bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables([Data, DataIndex])
        with test_db.atomic():
            number = 7540
            title = "Hypertext Transfer Protocol 2 (HTTP/2)"
            text = """This specification describes an optimized expression of 
            the semantics of the Hypertext Transfer Protocol (HTTP), referred 
            to as HTTP version 2 (HTTP/2).  HTTP/2 enables a more efficient 
            use of network"""
            category = "Standards Track"
            bookmark = True
            Data.create(
                number=number,
                title=title,
                text=text,
                category=category,
                bookmark=bookmark,
            )
            DataIndex.create(rowid=number, title=title, text=text, category=category)

    def tearDown(self):
        test_db.drop_tables([Data, DataIndex])
        test_db.close()

    def test_db_connection(self):
        result = test_db.connect(reuse_if_open=True)
        self.assertFalse(result)

    def test_db_is_open(self):
        self.assertFalse(test_db.is_closed())

    def test_tables_exist(self):
        self.assertTrue(Data.table_exists())
        self.assertTrue(DataIndex.table_exists())

    def test_insert_new_rows(self):
        with test_db.atomic():
            number = 1918
            title = "Address Allocation for Private Internets"
            text = """For the purposes of this document, an enterprise is an entity
            autonomously operating a network using TCP/IP and in particular
            determining the addressing plan and address assignments within that
            network."""
            category = "Best Current Practice"
            bookmark = False
            Data.create(
                number=number,
                title=title,
                text=text,
                category=category,
                bookmark=bookmark,
            )
            DataIndex.create(rowid=number, title=title, text=text, category=category)

            expected_title = [
                "Hypertext Transfer Protocol 2 (HTTP/2)",
                "Address Allocation for Private Internets",
            ]

            expected_number = [1918, 7540]
            actual_title = list()
            actual_number = list()
            for row in Data.select():
                actual_title.append(row.title)
                actual_number.append(row.number)
            self.assertCountEqual(actual_title, expected_title)
            self.assertCountEqual(actual_number, expected_number)
            self.assertNotEqual(actual_number, [123, 345])

    def test_search_by_number(self):
        query = Data.select().where(Data.number == 7540)
        for result in query:
            self.assertTrue(result, "7540")

    def test_search_by_keyword(self):
        phrase = "HTTP"
        query = (
            Data.select()
            .join(DataIndex, on=(Data.number == DataIndex.rowid))
            .where(DataIndex.match(phrase))
            .order_by(DataIndex.bm25())
        )
        expected = "Hypertext Transfer Protocol 2 (HTTP/2)"
        for result in query:
            self.assertTrue(result.title, phrase)
            self.assertEqual(result.title, expected)
            self.assertNotEqual(result.title, "HTTPS")
            self.assertNotEqual(result.title, "DNS")

    def test_search_by_bookmark(self):
        query = Data.select().where(Data.bookmark == 1)
        for result in query:
            self.assertEqual(result.number, 7540)
            self.assertNotEqual(result.number, 8305)

    def test_bookmarker(self):
        with test_db.atomic():
            number = 6555
            title = "Happy Eyeballs test"
            text = "testing bookmark"
            category = "Best Current Practice"
            bookmark = False
            Data.create(
                number=number,
                title=title,
                text=text,
                category=category,
                bookmark=bookmark,
            )
            DataIndex.create(rowid=number, title=title, text=text, category=category)

        query = Data.select().where(Data.number == 6555)
        for result in query:
            self.assertEqual(result.bookmark, False)
            Data.insert(
                title=result.title,
                text=result.text,
                number=result.number,
                category=result.category,
                bookmark=1,
            ).on_conflict("replace").execute()
        new = Data.select().where(Data.number == 6555)
        for result in new:
            self.assertEqual(result.bookmark, True)

    def test_delete_bookmark(self):
        exists = Data.select().where(Data.bookmark == 1 and Data.number == 7540)
        for result in exists:
            self.assertEqual(result.bookmark, True)
            Data.insert(
                title=result.title,
                text=result.text,
                number=result.number,
                category=result.category,
                bookmark=0,
            ).on_conflict("replace").execute()
        new = Data.select().where(Data.bookmark == 1 and Data.number == 7540)
        for x in new:
            self.assertEqual(x.bookmark, False)

    def test_number_does_not_exist(self):
        query = Data.select().where(Data.number == 8305)
        for result in query:
            self.assertFalse(result, "7540")

    def test_keyword_search_returns_null(self):
        phrase = "wolf"
        query = (
            Data.select()
            .join(DataIndex, on=(Data.number == DataIndex.rowid))
            .where(DataIndex.match(phrase))
            .order_by(DataIndex.bm25())
        )
        for result in query:
            print(result.title)
            self.assertIsNone(result.title)
            self.assertEqual(result.title, "")


if __name__ == "__main__":
    unittest.main()
