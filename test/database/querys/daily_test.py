import random
import unittest
import pandas as pd
from datetime import datetime, timedelta
from database import MongoDailyReportQuery, PostgresDailyReportQuery, DailyReportFieldDatabase
from model import DailyReportFieldModel
from test import DatabaseMongoTest, DatabasePostgresTest, LayerTypeTest


def get_dialy_report() -> pd.DataFrame:
    """Get example dataframe daily report."""
    date = datetime.now() - timedelta(days=1)
    date = date.strftime("%Y-%m-%d")
    return pd.DataFrame(
        data=[
            {
                DailyReportFieldModel.date: date,
                DailyReportFieldModel.idLayer: str(random.randint(0, 1000)),
                DailyReportFieldModel.typeLayer: LayerTypeTest.BORDE,
                DailyReportFieldModel.inProm: 0,
                DailyReportFieldModel.outProm: 0,
                DailyReportFieldModel.inMax: 0,
                DailyReportFieldModel.outMax: 0
            },
            {
                DailyReportFieldModel.date: date,
                DailyReportFieldModel.idLayer: str(random.randint(0, 1000)),
                DailyReportFieldModel.typeLayer: LayerTypeTest.BORDE,
                DailyReportFieldModel.inProm: 1,
                DailyReportFieldModel.outProm: 1,
                DailyReportFieldModel.inMax: 1,
                DailyReportFieldModel.outMax: 1
            },
        ]
    )


class TestMongo(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def insert(self) -> list:
        """Insert data example in the Daily report table in the PostgreSQL."""
        report = get_dialy_report()
        first_record = report.iloc[0].to_dict()
        second_record = report.iloc[1].to_dict()
        self.test_database.insert(
            table=LayerTypeTest.DAILY_REPORT,
            data=first_record
        )
        self.test_database.insert(
            table=LayerTypeTest.DAILY_REPORT,
            data=second_record
        )
        return [first_record, second_record]


    def test_insert(self):
        """Test insert a new daily report in the MongoDB."""
        database = MongoDailyReportQuery()
        response = database.new_report(data=get_dialy_report())
        self.test_database.clean(table=LayerTypeTest.DAILY_REPORT)

        self.assertTrue(response)

    def test_get(self):
        """Test get a daily report in the MongoDB."""
        example_report = self.insert()[0]
        database = MongoDailyReportQuery()
        response = database.get_report(
            layer_type=example_report[DailyReportFieldModel.typeLayer],
            date=example_report[DailyReportFieldModel.date]
        )
        self.test_database.clean(table=LayerTypeTest.DAILY_REPORT)

        self.assertFalse(response.empty)
        self.assertEqual(response[DailyReportFieldModel.date].iloc[0], example_report[DailyReportFieldModel.date])
        self.assertEqual(response[DailyReportFieldModel.typeLayer].iloc[0], example_report[DailyReportFieldModel.typeLayer])

        
class TestPostgres(unittest.TestCase):
    test_database: DatabasePostgresTest = DatabasePostgresTest()

    def create_table(self) -> None:
        """Create Daily report table in the PostgreSQL if does not exist."""
        self.test_database.create(
            table=LayerTypeTest.DAILY_REPORT,
            query=f"""
                ({DailyReportFieldDatabase.DATE} DATE NOT NULL,
                    {DailyReportFieldDatabase.ID_LAYER} INTEGER NOT NULL,
                    {DailyReportFieldDatabase.TYPE_LAYER} VARCHAR(15) NOT NULL,
                    {DailyReportFieldDatabase.IN_PROM} REAL NOT NULL,
                    {DailyReportFieldDatabase.IN_MAX} REAL NOT NULL,
                    {DailyReportFieldDatabase.OUT_PROM} REAL NOT NULL,
                    {DailyReportFieldDatabase.OUT_MAX} REAL NOT NULL,
                    CONSTRAINT {LayerTypeTest.DAILY_REPORT}_unique UNIQUE ({DailyReportFieldDatabase.DATE}, {DailyReportFieldDatabase.ID_LAYER})
                )
            """
        )

    def insert(self) -> list:
        """Insert data example in the Daily report table in the PostgreSQL."""
        report = get_dialy_report()
        first_record = report.iloc[0].to_dict()
        second_record = report.iloc[1].to_dict()
        self.create_table()
        self.test_database.insert(
            table=LayerTypeTest.DAILY_REPORT, 
            query=f"""
                ({DailyReportFieldDatabase.DATE}, 
                    {DailyReportFieldDatabase.ID_LAYER}, 
                    {DailyReportFieldDatabase.TYPE_LAYER}, 
                    {DailyReportFieldDatabase.IN_PROM}, 
                    {DailyReportFieldDatabase.OUT_PROM}, 
                    {DailyReportFieldDatabase.IN_MAX}, 
                    {DailyReportFieldDatabase.OUT_MAX}
                ) 
                VALUES (
                    '{first_record[DailyReportFieldModel.date]}',
                    {first_record[DailyReportFieldModel.idLayer]},
                    '{first_record[DailyReportFieldModel.typeLayer]}',
                    {first_record[DailyReportFieldModel.inProm]},
                    {first_record[DailyReportFieldModel.outProm]},
                    {first_record[DailyReportFieldModel.inMax]},
                    {first_record[DailyReportFieldModel.outMax]}
                )
            """
        )
        self.test_database.insert(
            table=LayerTypeTest.DAILY_REPORT, 
            query=f"""
                ({DailyReportFieldDatabase.DATE}, 
                    {DailyReportFieldDatabase.ID_LAYER}, 
                    {DailyReportFieldDatabase.TYPE_LAYER}, 
                    {DailyReportFieldDatabase.IN_PROM}, 
                    {DailyReportFieldDatabase.OUT_PROM}, 
                    {DailyReportFieldDatabase.IN_MAX}, 
                    {DailyReportFieldDatabase.OUT_MAX}
                ) 
                VALUES (
                    '{second_record[DailyReportFieldModel.date]}',
                    {second_record[DailyReportFieldModel.idLayer]},
                    '{second_record[DailyReportFieldModel.typeLayer]}',
                    {second_record[DailyReportFieldModel.inProm]},
                    {second_record[DailyReportFieldModel.outProm]},
                    {second_record[DailyReportFieldModel.inMax]},
                    {second_record[DailyReportFieldModel.outMax]}
                )
            """
        )
        return [first_record, second_record]

    def test_insert(self):
        """Test insert a new daily report in the PostgreSQL."""
        self.create_table()
        database = PostgresDailyReportQuery()
        response = database.new_report(data=get_dialy_report())
        self.test_database.clean(table=LayerTypeTest.DAILY_REPORT)

        self.assertTrue(response)

    def test_get(self):
        """Test get a daily report in the PostgreSQL."""
        example_report = self.insert()[0]
        database = PostgresDailyReportQuery()
        response = database.get_report(
            layer_type=example_report[DailyReportFieldModel.typeLayer],
            date=example_report[DailyReportFieldModel.date]
        )
        self.test_database.clean(table=LayerTypeTest.DAILY_REPORT)

        self.assertFalse(response.empty)
        self.assertEqual(response[DailyReportFieldModel.date].iloc[0], example_report[DailyReportFieldModel.date])
        self.assertEqual(response[DailyReportFieldModel.typeLayer].iloc[0], example_report[DailyReportFieldModel.typeLayer])

if __name__ == "__main__":
    unittest.main()