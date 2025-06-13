import unittest
from updater import BordeUpdaterHandler
from test import FileBordeDataTest, DatabaseBorderTest, DatabaseTrafficTest, ModelBordeType

class Test(unittest.TestCase):
    mongo_borde_db_test: DatabaseBorderTest = DatabaseBorderTest()
    postgres_borde_db_test: DatabaseBorderTest = DatabaseBorderTest(db_backup=True)
    mongo_traffic_db_test: DatabaseTrafficTest = DatabaseTrafficTest()
    postgres_traffic_db_test: DatabaseTrafficTest = DatabaseTrafficTest(db_backup=True)
    data_example: FileBordeDataTest = FileBordeDataTest(filename=f"{ModelBordeType.CISCO}%INTERFACE_TEST_1%10")

    def clean(self):
        self.data_example.delete_file()
        self.data_example.delete_father_folder()
        self.mongo_borde_db_test.clean()
        self.mongo_traffic_db_test.clean()
        self.postgres_borde_db_test.clean()
        self.postgres_traffic_db_test.clean()

    def test_get(self):
        """Test get all data from border files."""
        self.data_example.create_file()

        borderHandler = BordeUpdaterHandler()
        data = borderHandler.get_data(filepath=self.data_example.folder)
        print(data)
        self.assertEqual(type(data), list)
        self.assertTrue(data)
        
        self.clean()

    def test_load(self):
        """Test load all data from border files."""
        self.data_example.create_file()

        borderHandler = BordeUpdaterHandler()
        data = borderHandler.get_data(filepath=self.data_example.folder)
        status_operation = borderHandler._load_database(data=data, uri=self.mongo_borde_db_test.uri)
        self.assertTrue(status_operation)
        data_mongo = self.mongo_borde_db_test.get_all()
        self.assertEqual(len(data_mongo), 1)
        data_mongo = self.mongo_traffic_db_test.get_all()
        self.assertEqual(len(data_mongo), 3)
        
        status_operation = borderHandler._load_database(data=data, db_backup=True, uri=self.postgres_borde_db_test.uri)
        self.assertTrue(status_operation)
        data_postgres = self.postgres_borde_db_test.get_all()
        self.assertEqual(len(data_postgres), 1)
        data_postgres = self.postgres_traffic_db_test.get_all()
        self.assertEqual(len(data_postgres), 3)

        self.clean()
    

if __name__ == "__main__":
    unittest.main()