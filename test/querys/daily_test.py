import unittest
import pandas as pd
from database import DailyReportMongoQuery, PostgresDailyReportQuery
from model import DailyReportFieldModel
from test import DatabaseDailyTest, DailyReportModel


class Query(unittest.TestCase):
    mongo_db_test: DatabaseDailyTest = DatabaseDailyTest()
    postgres_db_test: DatabaseDailyTest = DatabaseDailyTest(db_backup=True)

    def model_to_dataframe(self, model: DailyReportModel) -> pd.DataFrame:
        """Transform model to dataframe."""
        data = {
            DailyReportFieldModel.date: [model.date],
            DailyReportFieldModel.idLayer: [model.idLayer],
            DailyReportFieldModel.typeLayer: [model.typeLayer],
            DailyReportFieldModel.inProm: [model.inProm],
            DailyReportFieldModel.outProm: [model.outProm],
            DailyReportFieldModel.inMax: [model.inMax],
            DailyReportFieldModel.outMax: [model.outMax]
        }
        return pd.DataFrame(data)

    def test_insert(self):
        """Test insert a new daily report in the MongoDB."""
        example_report = self.model_to_dataframe(self.mongo_db_test.get_exampĺe())
        database = DailyReportMongoQuery(uri=self.mongo_db_test.uri)
        response = database.new_report(data=example_report)
        self.mongo_db_test.clean()
        self.assertTrue(response)

        example_report = self.model_to_dataframe(self.postgres_db_test.get_exampĺe())
        database = PostgresDailyReportQuery(uri=self.postgres_db_test.uri)
        response = database.new_report(data=example_report)
        self.postgres_db_test.clean()
        self.assertTrue(response)

    def test_get(self):
        """Test get a daily report in the MongoDB."""
        example_report = self.mongo_db_test.insert()
        database = DailyReportMongoQuery(uri=self.mongo_db_test.uri)
        response = database.get_report(
            layer_type=example_report.typeLayer,
            date=example_report.date
        )
        print(response)
        self.mongo_db_test.clean()
        self.assertFalse(response.empty)
        self.assertEqual(response[DailyReportFieldModel.date].iloc[0], example_report.date)
        self.assertEqual(response[DailyReportFieldModel.typeLayer].iloc[0], example_report.typeLayer)

        example_report = self.postgres_db_test.insert()
        database = PostgresDailyReportQuery(uri=self.postgres_db_test.uri)
        response = database.get_report(
            layer_type=example_report.typeLayer,
            date=example_report.date
        )
        print(response)
        self.postgres_db_test.clean()
        self.assertFalse(response.empty)
        self.assertEqual(response[DailyReportFieldModel.date].iloc[0], example_report.date)
        self.assertEqual(response[DailyReportFieldModel.typeLayer].iloc[0], example_report.typeLayer)

if __name__ == "__main__":
    unittest.main()