import unittest
from constants.header import HeaderDataFrame
from handler import BrasHandler
from test import DatabaseBrasTest


class Handler(unittest.TestCase):
    mongo_db_test: DatabaseBrasTest = DatabaseBrasTest()
    postgres_db_test: DatabaseBrasTest = DatabaseBrasTest(db_backup=True)

    def test_get_all_interfaces(self):
        """Test get all interfaces of bras layer converted in a dataframe."""
        neccesary_columns = [
            HeaderDataFrame.ID, HeaderDataFrame.NAME,
            HeaderDataFrame.TYPE, HeaderDataFrame.CAPACITY
        ]

        self.mongo_db_test.insert()
        brasHandler = BrasHandler(uri=self.mongo_db_test.uri)
        data = brasHandler.get_all_interfaces()
        print(data)
        data_columns = data.columns.to_list()
        self.mongo_db_test.clean()
        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)

        self.postgres_db_test.insert()
        brasHandler = BrasHandler(db_backup=True, uri=self.postgres_db_test.uri)
        data = brasHandler.get_all_interfaces()
        print(data)
        data_columns = data.columns.to_list()
        self.postgres_db_test.clean()
        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


if __name__ == "__main__":
    unittest.main()