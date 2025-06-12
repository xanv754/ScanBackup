import unittest
from datetime import datetime
from pandas import DataFrame
from database import DailyReportFieldDatabase
from updater.handler.dailyReport import DailyReportUpdaterHandler
from test import FileDailyReportTest, DatabaseMongoTest, DatabasePostgresTest, LayerTypeTest


class Test(unittest.TestCase):
    test_database_mongo: DatabaseMongoTest = DatabaseMongoTest()
    test_database_postgres: DatabasePostgresTest = DatabasePostgresTest()


    def test_get_data(self):
        """Test get all data from daily report files."""
        data_example = FileDailyReportTest(filename="Resumen_Borde.csv")
        data_example.create_file()
        dailyReportHandler = DailyReportUpdaterHandler()
        data = dailyReportHandler.get_data(filepath=data_example.folder)
        data_example.delete_file()
        data_example.delete_father_folder()

        self.assertEqual(type(data), list)
        self.assertEqual(len(data), 1)
        self.assertEqual(type(data[0]), DataFrame)
        self.assertFalse(data[0].empty)
        

    def test_load_data(self):
        """Test load all data from daily report files."""
        data_example = FileDailyReportTest(filename="Resumen_Borde.csv")
        data_example.create_file()
        dailyReportHandler = DailyReportUpdaterHandler()
        data = dailyReportHandler.get_data(filepath=data_example.folder)
        response_mongo = dailyReportHandler._load_database(data=data)
        response_postgres = dailyReportHandler._load_database(data=data, db_backup=True)
        if response_mongo and response_postgres: response = True
        else: response = False
        daily_reports = self.test_database_mongo.get(table=LayerTypeTest.DAILY_REPORT, condition={DailyReportFieldDatabase.DATE: "2022-01-01"})

        data_example.delete_file()
        data_example.delete_father_folder()
        self.test_database_mongo.clean(table=LayerTypeTest.DAILY_REPORT)
        self.test_database_postgres.clean(table=LayerTypeTest.DAILY_REPORT)

        self.assertTrue(response)
        self.assertEqual(len(daily_reports), 1)
        self.assertEqual(daily_reports[0][DailyReportFieldDatabase.DATE], datetime.now().strftime("%Y-%m-%d"))


if __name__ == "__main__":
    unittest.main()