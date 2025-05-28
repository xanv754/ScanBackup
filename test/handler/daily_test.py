import random
import unittest
from datetime import datetime, timedelta
from constants.header import HeaderDataFrame
from database import DailyReportFieldDatabase, BordeFieldDatabase
from handler import DailyReportHandler
from model import DailyReportModel, BordeModel
from test import LayerTypeTest, DatabaseMongoTest, DatabasePostgresTest, ModelBordeTypeTest


def get_example_daily_report(id_layer: str = "", type_layer: str = "") -> DailyReportModel:
    """Get example daily report."""
    date = datetime.now() - timedelta(days=1)
    date = date.strftime("%Y-%m-%d")
    return DailyReportModel(
        date=date,
        idLayer=id_layer,
        typeLayer=type_layer,
        inProm=random.randint(0, 10),
        outProm=random.randint(0, 10),
        inMax=random.randint(0, 10),
        outMax=random.randint(0, 10)
    )

def get_example_interface() -> BordeModel:
    """Get example interface of borde layer."""
    return BordeModel(
        id=str(random.randint(0, 1000)),
        name="interface_test_" + str(random.randint(0, 1000)),
        model=ModelBordeTypeTest.HUAWEI,
        capacity=10,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )


class TestMongo(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def insert(self) -> None:
        """Insert data example in the Daily report table in the database."""
        first_interface = get_example_interface()
        first_interface.id = str(self.test_database.insert(table=LayerTypeTest.BORDE, data=first_interface.model_dump())["_id"])
        first_report = get_example_daily_report(id_layer=first_interface.id, type_layer=LayerTypeTest.BORDE)
        self.test_database.insert(table=LayerTypeTest.DAILY_REPORT, data=first_report.model_dump())
        second_interface = get_example_interface()
        second_interface.id = str(self.test_database.insert(table=LayerTypeTest.BORDE, data=second_interface.model_dump())["_id"])
        second_report = get_example_daily_report(id_layer=second_interface.id, type_layer=LayerTypeTest.BORDE)
        self.test_database.insert(table=LayerTypeTest.DAILY_REPORT, data=second_report.model_dump())
    
    def test_get_layer_borde(self):
        """Test get all daily report of a borde layer by a 1 day."""
        self.insert()
        daily_report_handler = DailyReportHandler()
        data = daily_report_handler.get_daily_report_by_days_before(
            layer_type=LayerTypeTest.BORDE,
            day_before=1
        )
        data_columns = data.columns.to_list()
        neccesary_columns = [
            HeaderDataFrame.INTERFACE,
            HeaderDataFrame.TYPE, 
            HeaderDataFrame.CAPACITY,
            HeaderDataFrame.DATE, 
            HeaderDataFrame.IN_PROM, 
            HeaderDataFrame.OUT_PROM, 
            HeaderDataFrame.IN_MAX, 
            HeaderDataFrame.OUT_MAX
        ]
        self.test_database.clean(table=LayerTypeTest.DAILY_REPORT)
        self.test_database.clean(table=LayerTypeTest.BORDE)

        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


class TestPostgres(unittest.TestCase):
    test_database: DatabasePostgresTest = DatabasePostgresTest()

    def create_table(self) -> None:
        """Create tables in the PostgreSQL if does not exist."""
        self.test_database.create(
            table=LayerTypeTest.BORDE,
            query=f"""
                ({BordeFieldDatabase.ID} INTEGER PRIMARY KEY,
                    {BordeFieldDatabase.NAME} VARCHAR(100) NOT NULL,
                    {BordeFieldDatabase.MODEL} VARCHAR(15) NOT NULL,
                    {BordeFieldDatabase.CAPACITY} SMALLINT NOT NULL,
                    {BordeFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE,
                    CONSTRAINT type_model CHECK (
                        {BordeFieldDatabase.MODEL} IN (
                            '{ModelBordeTypeTest.CISCO}',
                            '{ModelBordeTypeTest.HUAWEI}'
                        )
                    ),
                    CONSTRAINT {LayerTypeTest.BORDE}_unique UNIQUE ({BordeFieldDatabase.NAME}, {BordeFieldDatabase.MODEL})
                )
            """)
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

    def insert(self) -> None:
        """Insert data example in the borde and daily report table in the PostgreSQL."""
        first_interface = get_example_interface()
        self.create_table()
        self.test_database.insert(
            table=LayerTypeTest.BORDE, 
            query=f"""
                ({BordeFieldDatabase.ID}, 
                    {BordeFieldDatabase.NAME}, 
                    {BordeFieldDatabase.MODEL}, 
                    {BordeFieldDatabase.CAPACITY}
                ) 
                VALUES (
                    {int(first_interface.id)},
                    '{first_interface.name}',
                    '{first_interface.model}',
                    {first_interface.capacity}
                )
            """
        )
        first_report = get_example_daily_report(id_layer=first_interface.id, type_layer=LayerTypeTest.BORDE)
        self.test_database.insert(
            table=LayerTypeTest.DAILY_REPORT, 
            query=f"""
                ({DailyReportFieldDatabase.DATE}, 
                    {DailyReportFieldDatabase.ID_LAYER}, 
                    {DailyReportFieldDatabase.TYPE_LAYER}, 
                    {DailyReportFieldDatabase.IN_PROM}, 
                    {DailyReportFieldDatabase.IN_MAX}, 
                    {DailyReportFieldDatabase.OUT_PROM}, 
                    {DailyReportFieldDatabase.OUT_MAX}
                ) 
                VALUES (
                    '{first_report.date}',
                    {first_report.idLayer},
                    '{first_report.typeLayer}',
                    {first_report.inProm},
                    {first_report.inMax},
                    {first_report.outProm},
                    {first_report.outMax}
                )
            """
        )
        second_interface = get_example_interface()
        self.test_database.insert(
            table=LayerTypeTest.BORDE, 
            query=f"""
                ({BordeFieldDatabase.ID}, 
                    {BordeFieldDatabase.NAME}, 
                    {BordeFieldDatabase.MODEL}, 
                    {BordeFieldDatabase.CAPACITY}
                ) 
                VALUES (
                    {int(second_interface.id)},
                    '{second_interface.name}',
                    '{second_interface.model}',
                    {second_interface.capacity}
                )
            """
        )
        second_report = get_example_daily_report(id_layer=second_interface.id, type_layer=LayerTypeTest.BORDE)
        self.test_database.insert(
            table=LayerTypeTest.DAILY_REPORT, 
            query=f"""
                ({DailyReportFieldDatabase.DATE}, 
                    {DailyReportFieldDatabase.ID_LAYER}, 
                    {DailyReportFieldDatabase.TYPE_LAYER}, 
                    {DailyReportFieldDatabase.IN_PROM}, 
                    {DailyReportFieldDatabase.IN_MAX}, 
                    {DailyReportFieldDatabase.OUT_PROM}, 
                    {DailyReportFieldDatabase.OUT_MAX}
                ) 
                VALUES (
                    '{second_report.date}',
                    {second_report.idLayer},
                    '{second_report.typeLayer}',
                    {second_report.inProm},
                    {second_report.inMax},
                    {second_report.outProm},
                    {second_report.outMax}
                )
            """
        )

    def test_get_layer_borde(self):
        """Test get all daily report of a borde layer by a 1 day."""
        self.insert()
        daily_report_handler = DailyReportHandler(db_backup=True)
        data = daily_report_handler.get_daily_report_by_days_before(
            layer_type=LayerTypeTest.BORDE,
            day_before=1
        )
        data_columns = data.columns.to_list()
        neccesary_columns = [
            HeaderDataFrame.INTERFACE,
            HeaderDataFrame.TYPE, 
            HeaderDataFrame.CAPACITY,
            HeaderDataFrame.DATE, 
            HeaderDataFrame.IN_PROM, 
            HeaderDataFrame.OUT_PROM, 
            HeaderDataFrame.IN_MAX, 
            HeaderDataFrame.OUT_MAX
        ]
        self.test_database.clean(table=LayerTypeTest.DAILY_REPORT)
        self.test_database.clean(table=LayerTypeTest.BORDE)

        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)