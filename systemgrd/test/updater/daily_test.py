import unittest
from pandas import DataFrame
from systemgrd.updater import DailyReportUpdaterHandler
from systemgrd.test import FileDailyReportTest, DatabaseBorderTest, DatabaseDailyTest


class Updater(unittest.TestCase):
    borde_report_example: FileDailyReportTest = FileDailyReportTest(
        filename="Resumen_Borde.csv"
    )
    bras_report_example: FileDailyReportTest = FileDailyReportTest(
        filename="Resumen_Bras.csv"
    )
    mongo_borde_db_test: DatabaseDailyTest = DatabaseDailyTest()

    def clean(self):
        self.borde_report_example.delete_file()
        self.bras_report_example.delete_file()
        self.mongo_borde_db_test.clean()

    def test_get_data(self):
        """Test get all data from daily report files."""
        self.borde_report_example.create_file()
        self.bras_report_example.create_file()

        daily_handler = DailyReportUpdaterHandler()
        data = daily_handler.get_data(folderpath=self.borde_report_example.folder)
        print(data)
        self.assertEqual(type(data), DataFrame)
        self.assertFalse(data.empty)

        self.clean()

    def test_load_data(self):
        """Test load all data from daily report files."""
        self.borde_report_example.create_file()

        daily_handler = DailyReportUpdaterHandler()
        data = daily_handler.get_data(folderpath=self.borde_report_example.folder)
        response = daily_handler.load_data(data=data, uri=self.mongo_borde_db_test.uri)
        self.assertTrue(response)
        data_mongo = self.mongo_borde_db_test.get_all()
        self.assertEqual(len(data_mongo), 3)

        self.clean()


if __name__ == "__main__":
    unittest.main()
