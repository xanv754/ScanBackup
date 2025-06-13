import unittest
from constants.header import HeaderDataFrame
from handler import BordeHandler
from test import DatabaseBorderTest


class Handler(unittest.TestCase):
    mongo_db_test: DatabaseBorderTest = DatabaseBorderTest()
    postgres_db_test: DatabaseBorderTest = DatabaseBorderTest(db_backup=True)

    def test_get_all(self):
        """Test get all interfaces of borde layer converted in a dataframe."""
        neccesary_columns = [
            HeaderDataFrame.ID, HeaderDataFrame.NAME,
            HeaderDataFrame.MODEL, HeaderDataFrame.CAPACITY
        ]

        self.mongo_db_test.insert()
        bordeHandler = BordeHandler(uri=self.mongo_db_test.uri)
        data = bordeHandler.get_all_interfaces()
        print(data)
        data_columns = data.columns.to_list()
        self.mongo_db_test.clean()
        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)

        self.postgres_db_test.insert()
        bordeHandler = BordeHandler(db_backup=True, uri=self.postgres_db_test.uri)
        data = bordeHandler.get_all_interfaces()
        print(data)
        data_columns = data.columns.to_list()
        self.postgres_db_test.clean()
        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


if __name__ == "__main__":
    unittest.main()