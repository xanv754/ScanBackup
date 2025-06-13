import unittest
from constants.header import HeaderDataFrame
from handler import DailyReportHandler
from test import DatabaseDailyTest


class Handler(unittest.TestCase):
    mongo_db_test: DatabaseDailyTest = DatabaseDailyTest()
    postgres_db_test: DatabaseDailyTest = DatabaseDailyTest(db_backup=True)
    
    def test_get_layer_borde(self):
        """Test get all daily report of a borde layer by a 1 day."""
        neccesary_columns = [
            HeaderDataFrame.INTERFACE, HeaderDataFrame.TYPE, HeaderDataFrame.CAPACITY, 
            HeaderDataFrame.DATE, HeaderDataFrame.IN_PROM, HeaderDataFrame.OUT_PROM, 
            HeaderDataFrame.IN_MAX, HeaderDataFrame.OUT_MAX
        ]

        example_report = self.mongo_db_test.insert()
        daily_report_handler = DailyReportHandler(uri=self.mongo_db_test.uri)
        data = daily_report_handler.get_daily_report_by_days_before(layer_type=example_report.typeLayer, day_before=1)
        data_columns = data.columns.to_list()
        self.mongo_db_test.clean(border=True)
        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)

        example_report = self.postgres_db_test.insert()
        daily_report_handler = DailyReportHandler(db_backup=True, uri=self.postgres_db_test.uri)
        data = daily_report_handler.get_daily_report_by_days_before(layer_type=example_report.typeLayer, day_before=1)
        data_columns = data.columns.to_list()
        self.postgres_db_test.clean(border=True)
        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


if __name__ == "__main__":
    unittest.main()