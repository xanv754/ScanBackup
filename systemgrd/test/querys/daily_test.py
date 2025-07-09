import unittest
from database import DailyReportMongoQuery
from test import DatabaseDailyTest, DailyReportFieldName


class Query(unittest.TestCase):
    mongo_db_test: DatabaseDailyTest = DatabaseDailyTest()


    def test_insert(self):
        """Test insert a new daily report in the MongoDB."""
        example_report = self.mongo_db_test.get_exampĺe()
        database = DailyReportMongoQuery(uri=self.mongo_db_test.uri)
        response = database.new_report(data=[example_report])
        self.mongo_db_test.clean()
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
        self.assertEqual(response[DailyReportFieldName.DATE].iloc[0], example_report.date)
        self.assertEqual(response[DailyReportFieldName.TYPE_LAYER].iloc[0], example_report.typeLayer)


if __name__ == "__main__":
    unittest.main()