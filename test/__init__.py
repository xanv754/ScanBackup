import os
import random
import traceback
import psycopg2
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from dotenv import dotenv_values
from pydantic import BaseModel
from pymongo import MongoClient
from database import (
    BordeFieldDatabase, BrasFieldDatabase, CachingFieldDatabase, RaiFieldDatabase,
    TrafficHistoryFieldDatabase, IPHistoryFieldDatabase, DailyReportFieldDatabase,
    TableNameDatabase
)
from model import BordeModel, BrasModel, CachingModel, RaiModel, TrafficHistoryModel, DailyReportModel
from constants.group import ModelBordeType, BrasType, LayerType


class FileDataTest(ABC):
    filepath: str
    folder: str

    @abstractmethod
    def create_file(self) -> None:
        """Create a file with example data."""
        pass
    
    def delete_file(self) -> None:
        """Delete the example file."""
        if os.path.isfile(self.filepath):
            os.remove(self.filepath)
            if os.path.isdir(self.folder):
                os.rmdir(self.folder)

    @classmethod
    def delete_father_folder(cls) -> None:
        """Delete the father folder."""
        if os.path.isdir(f"{os.path.abspath(__file__).split('/test')[0]}/test/data/SCAN"):
            os.rmdir(f"{os.path.abspath(__file__).split('/test')[0]}/test/data/SCAN")
        if os.path.isdir(f"{os.path.abspath(__file__).split('/test')[0]}/test/data"):
            os.rmdir(f"{os.path.abspath(__file__).split('/test')[0]}/test/data")


class FileDataSCANTest(FileDataTest):

    def create_file(self) -> None:
        """Create a file with example data."""
        try:
            date = datetime.now() - timedelta(days=1)
            date = date.strftime("%Y-%m-%d")
            with open(self.filepath, "w") as file:
                file.write("Fecha Hora InPro OutPro InMax OutMax\n")
                file.write(f"{date} 17:35:00 11617614 2296806 11890501 2323927\n")
                file.write(f"{date} 20:55:00 3515418 2152241 3605922 2243843\n")
                file.write(f"{date} 23:50:00 2824666 2263704 3462229 2338423\n")
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

class FileBordeDataTest(FileDataSCANTest):
    def __init__(self, filename: str):
        filepath = f"{os.path.abspath(__file__).split('/test')[0]}/test/data/SCAN/Borde/{filename}"
        self.filepath = filepath
        self.folder = os.path.dirname(filepath)
        os.makedirs(self.folder, exist_ok=True)

 
class FileBrasDataTest(FileDataSCANTest):
    def __init__(self, filename: str):
        filepath = f"{os.path.abspath(__file__).split('/test')[0]}/test/data/SCAN/Bras/{filename}"
        self.filepath = filepath
        self.folder = os.path.dirname(filepath)


class FileCachingDataTest(FileDataSCANTest):
    def __init__(self, filename: str):
        filepath = f"{os.path.abspath(__file__).split('/test')[0]}/test/data/SCAN/Caching/{filename}"
        self.filepath = filepath
        self.folder = os.path.dirname(filepath)


class FileRaiDataTest(FileDataSCANTest):
    def __init__(self, filename: str):
        filepath = f"{os.path.abspath(__file__).split('/test')[0]}/test/data/SCAN/RAI/{filename}"
        self.filepath = filepath
        self.folder = os.path.dirname(filepath)


class FileDailyReportTest(FileDataTest):

    def __init__(self, filename: str):
        filepath = f"{os.path.abspath(__file__).split('/test')[0]}/test/data/SCAN/Reportes-Diarios/{filename}"
        self.filepath = filepath
        self.folder = os.path.dirname(filepath)
        os.makedirs(self.folder, exist_ok=True)

    def create_file(self) -> None:
        """Create a file with example data."""
        try:
            date = datetime.now() - timedelta(days=1)
            date = date.strftime("%Y-%m-%d")
            with open(self.filepath, "w") as file:
                file.write("Interfaz Tipo Fecha Capacidad In Out In-Max Out-Max Uso-%\n")
                file.write(f"Interfaz-1 HUAWEI {date} 10 11617614 2296806 11890501 2323927 98\n")
                file.write(f"Interfaz-2 HUAWEI {date} 10 3515418 2152241 3605922 2243843 60\n")
                file.write(f"Interfaz-3 HUAWEI {date} 10 2824666 2263704 3462229 2338423 50\n")
        except Exception as e:
            traceback.print_exc(e)
            exit(1)


class Database(ABC):
    uri: str
    name_db: str
    table: str
    db_backup: bool

    def __init__(self, table: str, db_backup: bool = False):
        try:
            if os.path.exists(".env.test"): env = dotenv_values(".env.test")
            else: raise FileNotFoundError("No file `env.test` with environment variables found")
            if db_backup:
                uri_postgres = env.get("URI_POSTGRES")
                if uri_postgres: self.uri = uri_postgres
                else: raise Exception("Failed to obtain configuration. URI PostgreSQL variable not found in enviroment file")
            else:
                uri_mongo = env.get("URI_MONGO")
                if uri_mongo: self.uri = uri_mongo
                else: raise Exception("Failed to obtain configuration. URI MongoDB variable not found in enviroment file")
            name_db = self.uri.split("/")[-1]
            self.name_db = name_db
            self.db_backup = db_backup
            self.table = table
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
        else:
            self.create_table()

    def clean(self) -> None:
        """Clean all registers in the database."""
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"DELETE FROM {self.table}")
                database.commit()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.table]
                collection.delete_many({})
                client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    @abstractmethod
    def get_exampĺe(self) -> BaseModel | None:
        """Get an example of data."""
        pass

    @abstractmethod
    def transform_model(self, data: dict | tuple) -> BaseModel | None:
        """Transform data to model."""
        pass

    @abstractmethod
    def create_table(self):
        """Insert a new register in the database."""
        pass

    @abstractmethod
    def insert(self, data: BaseModel) -> None:
        """Insert a new register in the database."""
        pass

    @abstractmethod
    def get(self, id: int) -> list:
        """Get one or more registers from the database."""
        pass

class DatabaseBorderTest(Database):
    def __init__(self, db_backup: bool = False):
        super().__init__(LayerType.BORDE, db_backup)

    def get_exampĺe(self) -> BordeModel | None:
        return BordeModel(
            id=str(random.randint(1, 100)),
            name=f"Interface_Test_{random.randint(1, 100)}",
            model=random.choice([ModelBordeType.CISCO, ModelBordeType.HUAWEI]),
            capacity=random.randint(1, 100),
            createAt=datetime.now().strftime("%Y-%m-%d")
        )

    def transform_model(self, data: dict | tuple) -> BordeModel | None:
        if isinstance(data, dict):
            return BordeModel(**data)
        elif isinstance(data, tuple):
            return BordeModel(id=str(data[0]), name=data[1], model=data[2], capacity=data[3], createAt=data[4].strftime("%Y-%m-%d"))
        else:
            return None

    def create_table(self) -> None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table} (
                        {BordeFieldDatabase.ID} VARCHAR(100) NULL,
                        {BordeFieldDatabase.NAME} VARCHAR(100) NOT NULL,
                        {BordeFieldDatabase.MODEL} VARCHAR(15) NOT NULL,
                        {BordeFieldDatabase.CAPACITY} SMALLINT NOT NULL,
                        {BordeFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE,
                        CONSTRAINT {self.table}_pkey PRIMARY KEY ({BordeFieldDatabase.NAME})
                    )"""
                )
                database.commit()
                database.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def insert(self, data: BordeModel | None = None) -> BordeModel:
        try:
            if data is None:
                data = self.get_exampĺe()
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    INSERT INTO {self.table} (
                        {BordeFieldDatabase.ID},
                        {BordeFieldDatabase.NAME},
                        {BordeFieldDatabase.MODEL},
                        {BordeFieldDatabase.CAPACITY}
                    ) VALUES ( %s, %s, %s, %s )
                """, (data.id, data.name, data.model, data.capacity))
                database.commit()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.table]
                collection.insert_one(data.model_dump())
                client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
        else:
            return data

    def get(self, id: int) -> BordeModel | None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    SELECT * 
                    FROM {self.table} 
                    WHERE {BordeFieldDatabase.ID} = %s""", (id,)
                )
                result = cursor.fetchone()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.table]
                result = collection.find_one({BordeFieldDatabase.ID: id})
                client.close()
            return self.transform_model(result)
        except Exception as e:
            traceback.print_exc(e)
            return []


class DatabaseBrasTest(Database):
    def __init__(self, db_backup: bool = False):
        super().__init__(LayerType.BRAS, db_backup)

    def get_exampĺe(self) -> BrasModel | None:
        return BrasModel(
            id=str(random.randint(1, 100)),
            name=f"Interface_Test_{random.randint(1, 100)}",
            type=random.choice([BrasType.UPLINK, BrasType.DOWNLINK]),
            capacity=random.randint(1, 100),
            createAt=datetime.now().strftime("%Y-%m-%d")
        )

    def transform_model(self, data: dict | tuple) -> BrasModel | None:
        if isinstance(data, dict):
            return BrasModel(**data)
        elif isinstance(data, tuple):
            return BrasModel(id=str(data[0]), name=data[1], type=data[2], capacity=data[3], createAt=data[4].strftime("%Y-%m-%d"))
        else:
            return None

    def create_table(self) -> None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table} (
                        {BrasFieldDatabase.ID} VARCHAR(100) NULL,
                        {BrasFieldDatabase.NAME} VARCHAR(100) NOT NULL,
                        {BrasFieldDatabase.TYPE} VARCHAR(15) NOT NULL,
                        {BrasFieldDatabase.CAPACITY} SMALLINT NOT NULL,
                        {BrasFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE,
                        CONSTRAINT {self.table}_pkey PRIMARY KEY ({BrasFieldDatabase.NAME})
                    )"""
                )
                database.commit()
                database.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def insert(self, data: BrasModel | None = None) -> BrasModel:
        try:
            if data is None:
                data = self.get_exampĺe()
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    INSERT INTO {self.table} (
                        {BrasFieldDatabase.ID},
                        {BrasFieldDatabase.NAME},
                        {BrasFieldDatabase.TYPE},
                        {BrasFieldDatabase.CAPACITY}
                    ) VALUES ( %s, %s, %s, %s )
                """, (data.id, data.name, data.type, data.capacity))
                database.commit()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.table]
                collection.insert_one(data.model_dump())
                client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
        else:
            return data

    def get(self, id: int) -> BrasModel | None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    SELECT * 
                    FROM {self.table} 
                    WHERE {BrasFieldDatabase.ID} = %s""", (id,)
                )
                result = cursor.fetchone()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.table]
                result = collection.find_one({BrasFieldDatabase.ID: id})
                client.close()
            return self.transform_model(result)
        except Exception as e:
            traceback.print_exc(e)
            return []


class DatabaseCachingTest(Database):
    def __init__(self, db_backup: bool = False):
        super().__init__(LayerType.CACHING, db_backup)

    def get_exampĺe(self) -> CachingModel | None:
        return CachingModel(
            id=str(random.randint(1, 100)),
            name=f"Interface_Test_{random.randint(1, 100)}",
            service="GOOGLE",
            capacity=random.randint(1, 100),
            createAt=datetime.now().strftime("%Y-%m-%d")
        )

    def transform_model(self, data: dict | tuple) -> CachingModel | None:
        if isinstance(data, dict):
            return CachingModel(**data)
        elif isinstance(data, tuple):
            return CachingModel(id=str(data[0]), name=data[1], service=data[2], capacity=data[3], createAt=data[4].strftime("%Y-%m-%d"))
        else:
            return None

    def create_table(self) -> None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table} (
                        {CachingFieldDatabase.ID} VARCHAR(100) NULL,
                        {CachingFieldDatabase.NAME} VARCHAR(100) NOT NULL,
                        {CachingFieldDatabase.SERVICE} VARCHAR(20) NOT NULL,
                        {CachingFieldDatabase.CAPACITY} SMALLINT NOT NULL,
                        {CachingFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE,
                        CONSTRAINT {self.table}_pkey PRIMARY KEY ({CachingFieldDatabase.NAME})
                    )"""
                )
                database.commit()
                database.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def insert(self, data: CachingModel | None = None) -> CachingModel:
        try:
            if data is None:
                data = self.get_exampĺe()
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    INSERT INTO {self.table} (
                        {CachingFieldDatabase.ID},
                        {CachingFieldDatabase.NAME},
                        {CachingFieldDatabase.SERVICE},
                        {CachingFieldDatabase.CAPACITY}
                    ) VALUES ( %s, %s, %s, %s )
                """, (data.id, data.name, data.service, data.capacity))
                database.commit()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.table]
                collection.insert_one(data.model_dump())
                client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
        else:
            return data

    def get(self, id: int) -> CachingModel | None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    SELECT * 
                    FROM {self.table} 
                    WHERE {CachingFieldDatabase.ID} = %s""", (id,)
                )
                result = cursor.fetchone()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.table]
                result = collection.find_one({CachingFieldDatabase.ID: id})
                client.close()
            return self.transform_model(result)
        except Exception as e:
            traceback.print_exc(e)
            return []
        

class DatabaseRaiTest(Database):
    def __init__(self, db_backup: bool = False):
        super().__init__(LayerType.RAI, db_backup)

    def get_exampĺe(self) -> RaiModel | None:
        return RaiModel(
            id=str(random.randint(1, 100)),
            name=f"Interface_Test_{random.randint(1, 100)}",
            capacity=random.randint(1, 100),
            createAt=datetime.now().strftime("%Y-%m-%d")
        )

    def transform_model(self, data: dict | tuple) -> RaiModel | None:
        if isinstance(data, dict):
            return RaiModel(**data)
        elif isinstance(data, tuple):
            return RaiModel(id=str(data[0]), name=data[1], capacity=data[2], createAt=data[3].strftime("%Y-%m-%d"))
        else:
            return None

    def create_table(self) -> None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table} (
                        {RaiFieldDatabase.ID} VARCHAR(100) NULL,
                        {RaiFieldDatabase.NAME} VARCHAR(150) NOT NULL,
                        {RaiFieldDatabase.CAPACITY} REAL NOT NULL,
                        {RaiFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE,
                        CONSTRAINT {self.table}_pkey PRIMARY KEY ({RaiFieldDatabase.NAME})
                    )"""
                )
                database.commit()
                database.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def insert(self, data: RaiModel | None = None) -> RaiModel:
        try:
            if data is None:
                data = self.get_exampĺe()
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    INSERT INTO {self.table} (
                        {RaiFieldDatabase.ID},
                        {RaiFieldDatabase.NAME},
                        {RaiFieldDatabase.CAPACITY}
                    ) VALUES ( %s, %s, %s )
                """, (data.id, data.name, data.capacity))
                database.commit()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.table]
                collection.insert_one(data.model_dump())
                client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
        else:
            return data

    def get(self, id: int) -> RaiModel | None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    SELECT * 
                    FROM {self.table} 
                    WHERE {RaiFieldDatabase.ID} = %s""", (id,)
                )
                result = cursor.fetchone()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.table]
                result = collection.find_one({RaiFieldDatabase.ID: id})
                client.close()
            return self.transform_model(result)
        except Exception as e:
            traceback.print_exc(e)
            return []
        

class DatabaseTrafficTest(Database):
    def __init__(self, db_backup: bool = False):
        super().__init__(LayerType.TRAFFIC_HISTORY, db_backup)

    def get_exampĺe(self) -> TrafficHistoryModel | None:
        return TrafficHistoryModel(
            date=datetime.now().strftime("%Y-%m-%d"),
            time=datetime.now().strftime("%H:%M:%S"),
            idLayer=str(random.randint(0, 1000)),
            typeLayer=random.choice([LayerType.BORDE, LayerType.BRAS, LayerType.CACHING, LayerType.RAI]),
            inProm=random.randint(1, 100),
            outProm=random.randint(1, 100),
            inMax=random.randint(1, 100),
            outMax=random.randint(1, 100)
        )

    def transform_model(self, data: dict | tuple) -> TrafficHistoryModel | None:
        if isinstance(data, dict):
            return TrafficHistoryModel(**data)
        elif isinstance(data, tuple):
            return TrafficHistoryModel(
                date=data[0].strftime("%Y-%m-%d"),
                time=data[1].strftime("%H:%M:%S"),
                idLayer=str(data[2]),
                typeLayer=data[3],
                inProm=data[4],
                outProm=data[5],
                inMax=data[6],
                outMax=data[7]
            )
        else:
            return None

    def create_table(self) -> None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {TableNameDatabase.TRAFFIC_HISTORY} (
                        {TrafficHistoryFieldDatabase.DATE} DATE NOT NULL,
                        {TrafficHistoryFieldDatabase.TIME} TIME NOT NULL,
                        {TrafficHistoryFieldDatabase.ID_LAYER} VARCHAR(100) NOT NULL,
                        {TrafficHistoryFieldDatabase.TYPE_LAYER} VARCHAR(15) NOT NULL,
                        {TrafficHistoryFieldDatabase.IN_PROM} REAL NOT NULL,
                        {TrafficHistoryFieldDatabase.OUT_PROM} REAL NOT NULL,
                        {TrafficHistoryFieldDatabase.IN_MAX} REAL NOT NULL,
                        {TrafficHistoryFieldDatabase.OUT_MAX} REAL NOT NULL,
                        CONSTRAINT {TableNameDatabase.TRAFFIC_HISTORY}_pkey PRIMARY KEY (
                            {TrafficHistoryFieldDatabase.DATE}, 
                            {TrafficHistoryFieldDatabase.TIME}, 
                            {TrafficHistoryFieldDatabase.ID_LAYER},
                            {TrafficHistoryFieldDatabase.TYPE_LAYER}
                        )
                    )"""
                )
                database.commit()
                database.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def insert(self, data: TrafficHistoryModel | None = None) -> TrafficHistoryModel:
        try:
            if data is None:
                data = self.get_exampĺe()
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    INSERT INTO {self.table} (
                        {TrafficHistoryFieldDatabase.DATE},
                        {TrafficHistoryFieldDatabase.TIME},
                        {TrafficHistoryFieldDatabase.ID_LAYER},
                        {TrafficHistoryFieldDatabase.TYPE_LAYER},
                        {TrafficHistoryFieldDatabase.IN_PROM},
                        {TrafficHistoryFieldDatabase.OUT_PROM},
                        {TrafficHistoryFieldDatabase.IN_MAX},
                        {TrafficHistoryFieldDatabase.OUT_MAX}
                    ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s )
                """, (data.date, data.time, data.idLayer, data.typeLayer, data.inProm, data.outProm, data.inMax, data.outMax))
                database.commit()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.table]
                collection.insert_one(data.model_dump())
                client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
        else:
            return data

    def get(self, date: str, idLayer: str, typeLayer: str) -> TrafficHistoryModel | None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    SELECT * 
                    FROM {self.table} 
                    WHERE {TrafficHistoryFieldDatabase.DATE} = %s AND
                    {TrafficHistoryFieldDatabase.ID_LAYER} = %s AND
                    {TrafficHistoryFieldDatabase.TYPE_LAYER} = %s
                """, (date, idLayer, typeLayer))
                result = cursor.fetchone()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.table]
                result = collection.find_one({
                    TrafficHistoryFieldDatabase.DATE: date,
                    TrafficHistoryFieldDatabase.ID_LAYER: idLayer,
                    TrafficHistoryFieldDatabase.TYPE_LAYER: typeLayer
                })
                client.close()
            return self.transform_model(result)
        except Exception as e:
            traceback.print_exc(e)
            return []
        

class DatabaseDailyTest(Database):
    def __init__(self, db_backup: bool = False):
        super().__init__(LayerType.DAILY_REPORT, db_backup=db_backup)

    def get_exampĺe(self) -> DailyReportModel | None:
        return DailyReportModel(
            date=datetime.now().strftime("%Y-%m-%d"),
            idLayer=str(random.randint(1, 100)),
            typeLayer=random.choice([LayerType.BORDE, LayerType.BRAS, LayerType.CACHING, LayerType.RAI]),
            inProm=random.randint(1, 100),
            outProm=random.randint(1, 100),
            inMax=random.randint(1, 100),
            outMax=random.randint(1, 100)
        )

    def transform_model(self, data: dict | tuple) -> DailyReportModel | None:
        if isinstance(data, dict):
            return DailyReportModel(**data)
        elif isinstance(data, tuple):
            return DailyReportModel(
                date=data[0].strftime("%Y-%m-%d"),
                idLayer=str(data[1]),
                typeLayer=data[2],
                inProm=data[3],
                outProm=data[4],
                inMax=data[5],
                outMax=data[6]
            )
        else:
            return None

    def create_table(self) -> None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {TableNameDatabase.DAILY_REPORT} (
                        {DailyReportFieldDatabase.DATE} DATE NOT NULL,
                        {DailyReportFieldDatabase.ID_LAYER} INTEGER NOT NULL,
                        {DailyReportFieldDatabase.TYPE_LAYER} VARCHAR(15) NOT NULL,
                        {DailyReportFieldDatabase.IN_PROM} REAL NOT NULL,
                        {DailyReportFieldDatabase.OUT_PROM} REAL NOT NULL,
                        {DailyReportFieldDatabase.IN_MAX} REAL NOT NULL,
                        {DailyReportFieldDatabase.OUT_MAX} REAL NOT NULL,
                        CONSTRAINT {TableNameDatabase.DAILY_REPORT}_pkey PRIMARY KEY (
                            {DailyReportFieldDatabase.DATE}, 
                            {DailyReportFieldDatabase.ID_LAYER}
                        )
                    )""" 
                )
                database.commit()
                database.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def insert(self, data: DailyReportModel | None = None) -> DailyReportModel:
        try:
            if data is None:
                data = self.get_exampĺe()
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    INSERT INTO {self.table} (
                        {DailyReportFieldDatabase.DATE},
                        {DailyReportFieldDatabase.ID_LAYER},
                        {DailyReportFieldDatabase.TYPE_LAYER},
                        {DailyReportFieldDatabase.IN_PROM},
                        {DailyReportFieldDatabase.OUT_PROM},
                        {DailyReportFieldDatabase.IN_MAX},
                        {DailyReportFieldDatabase.OUT_MAX}
                    ) VALUES ( %s, %s, %s, %s, %s, %s, %s )
                """, (data.date, data.idLayer, data.typeLayer, data.inProm, data.outProm, data.inMax, data.outMax))
                database.commit()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.table]
                collection.insert_one(data.model_dump())
                client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
        else:
            return data

    def get(self, date: str, idLayer: str, typeLayer: str) -> DailyReportModel | None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    SELECT * 
                    FROM {self.table} 
                    WHERE {DailyReportFieldDatabase.DATE} = %s AND
                    {DailyReportFieldDatabase.ID_LAYER} = %s AND
                    {DailyReportFieldDatabase.TYPE_LAYER} = %s
                """, (date, idLayer, typeLayer))
                result = cursor.fetchone()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.table]
                result = collection.find_one({
                    DailyReportFieldDatabase.DATE: date,
                    DailyReportFieldDatabase.ID_LAYER: idLayer,
                    DailyReportFieldDatabase.TYPE_LAYER: typeLayer
                })
                client.close()
            return self.transform_model(result)
        except Exception as e:
            traceback.print_exc(e)
            return []


if __name__ == "__main__":
    borde_example = BordeModel(id="1", name="INTERFACE_TEST_BORDE_1", model=ModelBordeType.CISCO, capacity=10, createAt=datetime.now().strftime("%Y-%m-%d"))
    mongo = DatabaseBorderTest()
    mongo.create_table()
    mongo.insert(data=borde_example)
    response = mongo.get(id="1")
    print(response)
    mongo.clean()

    postgres = DatabaseBorderTest(db_backup=True)
    postgres.create_table()
    postgres.insert(data=borde_example)
    response = postgres.get(id="1")
    print(response)
    postgres.clean()

    bras_example = BrasModel(id="1", name="INTERFACE_TEST_BRAS_1", type=BrasType.UPLINK, capacity=10, createAt=datetime.now().strftime("%Y-%m-%d"))
    mongo = DatabaseBrasTest()
    mongo.create_table()
    mongo.insert(data=bras_example)
    response = mongo.get(id="1")
    print(response)
    mongo.clean()

    postgres = DatabaseBrasTest(db_backup=True)
    postgres.create_table()
    postgres.insert(data=bras_example)
    response = postgres.get(id="1")
    print(response)
    postgres.clean()

    caching_example = CachingModel(id="1", name="INTERFACE_TEST_CACHING_1", service="GOOGLE", capacity=10, createAt=datetime.now().strftime("%Y-%m-%d"))
    mongo = DatabaseCachingTest()
    mongo.create_table()
    mongo.insert(data=caching_example)
    response = mongo.get(id="1")
    print(response)
    mongo.clean()

    postgres = DatabaseCachingTest(db_backup=True)
    postgres.create_table()
    postgres.insert(data=caching_example)
    response = postgres.get(id="1")
    print(response)
    postgres.clean()

    rai_example = RaiModel(id="1", name="INTERFACE_TEST_RAI_1", capacity=10, createAt=datetime.now().strftime("%Y-%m-%d"))
    mongo = DatabaseRaiTest()
    mongo.create_table()
    mongo.insert(data=rai_example)
    response = mongo.get(id="1")
    print(response)
    mongo.clean()

    postgres = DatabaseRaiTest(db_backup=True)
    postgres.create_table()
    postgres.insert(data=rai_example)
    response = postgres.get(id="1")
    print(response)
    postgres.clean()

    traffic_example = TrafficHistoryModel(
        date=datetime.now().strftime("%Y-%m-%d"),
        time=datetime.now().strftime("%H:%M:%S"),
        idLayer="1",
        typeLayer="BORDE",
        inProm=10,
        outProm=10,
        inMax=10,
        outMax=10
    )
    mongo = DatabaseTrafficTest()
    mongo.create_table()
    mongo.insert(data=traffic_example)
    response = mongo.get(date=traffic_example.date, idLayer=traffic_example.idLayer, typeLayer=traffic_example.typeLayer)
    print(response)
    mongo.clean()

    postgres = DatabaseTrafficTest(db_backup=True)
    postgres.create_table()
    postgres.insert(data=traffic_example)
    response = postgres.get(date=traffic_example.date, idLayer=traffic_example.idLayer, typeLayer=traffic_example.typeLayer)
    print(response)
    postgres.clean()

    daily_example = DailyReportModel(
        date=datetime.now().strftime("%Y-%m-%d"),
        idLayer="1",
        typeLayer="BORDE",
        inProm=10,
        outProm=10,
        inMax=10,
        outMax=10
    )
    mongo = DatabaseDailyTest()
    mongo.create_table()
    mongo.insert(data=daily_example)
    response = mongo.get(date=daily_example.date, idLayer=daily_example.idLayer, typeLayer=daily_example.typeLayer)
    print(response)
    mongo.clean()

    postgres = DatabaseDailyTest(db_backup=True)
    postgres.create_table()
    postgres.insert(data=daily_example)
    response = postgres.get(date=daily_example.date, idLayer=daily_example.idLayer, typeLayer=daily_example.typeLayer)
    print(response)
    postgres.clean()

    data_scan = FileBordeDataTest(filename="CISCO%INTERFACE_TEST_1%10")
    data_scan.create_file()
    data_scan.delete_file()

    data_daily_report = FileDailyReportTest(filename="Resumen_Borde.csv")
    data_daily_report.create_file()
    data_daily_report.delete_file()