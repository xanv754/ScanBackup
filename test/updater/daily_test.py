import unittest
import random
from pandas import DataFrame
from updater import DailyReportUpdaterHandler
from test import FileDailyReportTest, DatabaseBorderTest, BordeModel


class Test(unittest.TestCase):
    borde_report_example: FileDailyReportTest = FileDailyReportTest(filename="Resumen_Borde.csv")
    bras_report_example: FileDailyReportTest = FileDailyReportTest(filename="Resumen_Bras.csv")
    mongo_borde_db_test: DatabaseBorderTest = DatabaseBorderTest()
    postgres_borde_db_test: DatabaseBorderTest = DatabaseBorderTest(db_backup=True)

    def clean(self):
        self.borde_report_example.delete_file()
        self.bras_report_example.delete_file()
        self.borde_report_example.delete_father_folder()
        self.bras_report_example.delete_father_folder()
        self.mongo_borde_db_test.clean()
        self.postgres_borde_db_test.clean()

    def insert_interfaces(self, data: DataFrame, db_backup: bool = False) -> None:
        for _index, row in data.iterrows():
            data_example = BordeModel(
                id=str(random.randint(1, 100)),
                name=row["interface"],
                model=row["type"],
                capacity=row["capacity"],
                createAt=row["date"]
            )
            if db_backup:
                self.postgres_borde_db_test.insert(data=data_example)
            else:
                self.mongo_borde_db_test.insert(data=data_example)

    def test_get_data(self):
        """Test get all data from daily report files."""
        self.borde_report_example.create_file()
        self.bras_report_example.create_file()

        daily_handler = DailyReportUpdaterHandler()
        data = daily_handler.get_data(folderpath=self.borde_report_example.folder)
        print(data)
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), 2)
        self.assertEqual(type(data[0]), DataFrame)

        self.clean()

    def test_load_data(self):
        """Test load all data from daily report files."""
        self.borde_report_example.create_file()

        daily_handler = DailyReportUpdaterHandler()
        data = daily_handler.get_data(folderpath=self.borde_report_example.folder)
        print(data)

        self.insert_interfaces(data[0])

        response = daily_handler._load_database(data=data, uri=self.mongo_borde_db_test.uri)
        self.assertTrue(response)

        self.clean()



if __name__ == "__main__":
    unittest.main()
