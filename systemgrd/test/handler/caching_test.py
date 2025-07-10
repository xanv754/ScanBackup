import unittest
from systemgrd.handler import CachingHandler
from systemgrd.test import DatabaseCachingTest, DatabaseDailyTest


class Handler(unittest.TestCase):
    interface_db_test: DatabaseCachingTest = DatabaseCachingTest()
    daily_db_test: DatabaseDailyTest = DatabaseDailyTest()

    def test_get_interfaces(self):
        """Test get all interfaces of caching layer converted in a dataframe."""
        self.interface_db_test.insert()
        handler = CachingHandler(uri=self.interface_db_test.uri)
        data = handler.get_all_interfaces()
        print(data)
        self.interface_db_test.clean()
        self.assertFalse(data.empty)

    def test_get_daily_report(self):
        """Test get all daily report of caching layer converted in a dataframe."""
        self.daily_db_test.insert(caching=True)
        handler = CachingHandler(uri=self.daily_db_test.uri)
        data = handler.get_all_daily_report()
        print(data)
        self.daily_db_test.clean()
        self.assertFalse(data.empty)


if __name__ == "__main__":
    unittest.main()