import unittest
from datetime import datetime, timedelta
from systemgrd.handler import BBIPHandler
from systemgrd.test import DatabaseDailyTest, DatabaseBorderTest, DatabaseBrasTest, DatabaseCachingTest, DatabaseRaiTest


class Handler(unittest.TestCase):
    daily_db_test: DatabaseDailyTest = DatabaseDailyTest()
    borde_db_test: DatabaseBorderTest = DatabaseBorderTest()
    bras_db_test: DatabaseBrasTest = DatabaseBrasTest()
    caching_db_test: DatabaseCachingTest = DatabaseCachingTest()
    rai_db_test: DatabaseRaiTest = DatabaseRaiTest()

    def clean(self):
        self.daily_db_test.clean()
        self.borde_db_test.clean()
        self.bras_db_test.clean()
        self.caching_db_test.clean()
        self.rai_db_test.clean()
    
    def test_get_all_interfaces(self):
        """Test get all interfaces."""
        self.borde_db_test.insert()
        self.bras_db_test.insert()
        self.caching_db_test.insert()
        self.rai_db_test.insert()

        handler = BBIPHandler(uri=self.daily_db_test.uri)
        data = handler.get_all_interfaces()
        print(data)
        self.assertFalse(data.empty)

        self.clean()

    def test_get_all_interfaces_by_date(self):
        """Test get all interfaces by a date."""
        self.borde_db_test.insert()
        self.bras_db_test.insert()
        self.caching_db_test.insert()
        self.rai_db_test.insert()

        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        handler = BBIPHandler(uri=self.daily_db_test.uri)
        data = handler.get_all_interfaces_by_date(date=date)
        print(data)
        self.assertFalse(data.empty)
        
        self.clean()

    def test_get_all_daily_report(self):
        """Test get all daily report."""
        self.daily_db_test.insert(borde=True)
        self.daily_db_test.insert(bras=True)
        self.daily_db_test.insert(caching=True)
        self.daily_db_test.insert(rai=True)
        
        handler = BBIPHandler(uri=self.daily_db_test.uri)
        data = handler.get_all_daily_report_by_date()
        print(data)
        self.assertFalse(data.empty)    

        self.clean()
        
    def test_get_all_daily_report_by_days_before(self):
        """Test get all daily report by days before."""
        self.daily_db_test.insert(borde=True)
        self.daily_db_test.insert(bras=True)
        self.daily_db_test.insert(caching=True)
        self.daily_db_test.insert(rai=True)

        handler = BBIPHandler(uri=self.daily_db_test.uri)
        data = handler.get_all_daily_data_by_days_before(day_before=1)
        print(data)
        self.assertFalse(data.empty)

        self.clean()


if __name__ == "__main__":
    unittest.main()