import os
import shutil
import traceback
import psycopg2
from typing import List
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
from model import BordeModel
from constants.group import ModelBordeType as ModelBordeTypeTest
from constants.group import BrasType as BrasTypeTest
from database.constant.tables import TableNameDatabase as LayerTypeTest
from database.constant.fields import TrafficHistoryFieldDatabase as TrafficFieldDatabaseTest


class DatabaseTest(ABC):
    uri: str
    name_db: str

    @abstractmethod
    def clean(self, table) -> None:
        """Clean all registers in the database."""
        pass

    @abstractmethod
    def insert(self, table, data):
        """Insert a new register in the database."""
        pass

    @abstractmethod
    def get(self, table, condition) -> list:
        """Get one or more registers from the database."""
        pass


class DatabaseMongoTest(DatabaseTest):
    def __init__(self):
        try:
            if os.path.exists(".env.test"): env = dotenv_values(".env.test")
            else: raise FileNotFoundError("No file `env.test` with environment variables found")
            uri_mongo = env.get("URI_MONGO")
            if uri_mongo: self.uri = uri_mongo
            else: raise Exception("Failed to obtain configuration. URI MongoDB variable not found in enviroment file")
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
        else:
            name_db = self.uri.split("/")[-1]
            self.name_db = name_db


    def clean(self, table: str) -> None:
        try:
            client = MongoClient(self.uri)
            database = client[self.name_db]
            collection = database[table]
            collection.delete_many({})
            client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
            
    def insert(self, table: str, data: dict) -> dict:
        try:
            client = MongoClient(self.uri)
            database = client[self.name_db]
            collection = database[table]
            response = collection.insert_one(data)
            id = response.inserted_id
            data = collection.find_one({"_id": id})
            client.close()
            return data
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def get(self, table: str, condition: dict) -> List[dict]:
        try:
            response = []
            client = MongoClient(self.uri)
            database = client[self.name_db]
            collection = database[table]
            cursor = collection.find(condition)
            if cursor:
                for data in cursor:
                    response.append(data)
            client.close()
            return response
        except Exception as e:
            traceback.print_exc(e)
            return []


class DatabasePostgresTest(DatabaseTest):
    __table_created: bool = False

    def __init__(self):
        try:
            if os.path.exists(".env.test"): env = dotenv_values(".env.test")
            else: raise FileNotFoundError("No file `env.test` with environment variables found")
            uri_postgres = env.get("URI_POSTGRES")
            if uri_postgres: self.uri = uri_postgres
            else: raise Exception("Failed to obtain configuration. URI PostgreSQL variable not found in enviroment file")
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
        else:
            name_db = self.uri.split("/")[-1]
            self.name_db = name_db

    def create(self, table: str, query: str) -> None:
        try:
            if not self.__table_created:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} {query}")
                database.commit()
                database.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
        else:
            self.__table_created = True

    def clean(self, table: str) -> None:
        try:
            database = psycopg2.connect(self.uri)
            cursor = database.cursor()
            cursor.execute(f"DELETE FROM {table}")
            database.commit()
            database.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def insert(self, table: str, query: str) -> bool:
        try:
            database = psycopg2.connect(self.uri)
            cursor = database.cursor()
            cursor.execute(f"INSERT INTO {table} {query}")
            database.commit()
            status = cursor.statusmessage
            database.close()
            return status == "INSERT 0 1"
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def get(self, name_collection: str, condition: str) -> List[tuple]:
        try:
            database = psycopg2.connect(self.uri)
            cursor = database.cursor()
            cursor.execute(f"SELECT * FROM {name_collection} WHERE {condition}")
            result = cursor.fetchall()
            database.close()
            return result
        except Exception as e:
            traceback.print_exc(e)
            return []


class FileDataTest(ABC):
    filepath: str
    folder: str

    def create_file(self) -> None:
        """Create a file with example data."""
        if os.path.isdir(f"{os.path.abspath(__file__).split('/test')[0]}/test/data"):
            shutil.rmtree(f"{os.path.abspath(__file__).split('/test')[0]}/test/data")
        os.makedirs(self.folder, exist_ok=True)
        date = datetime.now() - timedelta(days=1)
        date = date.strftime("%Y-%m-%d")
        with open(self.filepath, "w") as file:
            file.write("Fecha Hora InPro OutPro InMax OutMax\n")
            file.write(f"{date} 17:35:00 11617614 2296806 11890501 2323927\n")
            file.write(f"{date} 20:55:00 3515418 2152241 3605922 2243843\n")
            file.write(f"{date} 23:50:00 2824666 2263704 3462229 2338423\n")
    
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


class FileBordeDataTest(FileDataTest):
    def __init__(self, filename: str):
        filepath = f"{os.path.abspath(__file__).split('/test')[0]}/test/data/SCAN/Borde/{filename}"
        self.filepath = filepath
        self.folder = os.path.dirname(filepath)

 
class FileBrasDataTest(FileDataTest):
    def __init__(self, filename: str):
        filepath = f"{os.path.abspath(__file__).split('/test')[0]}/test/data/SCAN/Bras/{filename}"
        self.filepath = filepath
        self.folder = os.path.dirname(filepath)


class FileCachingDataTest(FileDataTest):
    def __init__(self, filename: str):
        filepath = f"{os.path.abspath(__file__).split('/test')[0]}/test/data/SCAN/Caching/{filename}"
        self.filepath = filepath
        self.folder = os.path.dirname(filepath)


class FileRaiDataTest(FileDataTest):
    def __init__(self, filename: str):
        filepath = f"{os.path.abspath(__file__).split('/test')[0]}/test/data/SCAN/RAI/{filename}"
        self.filepath = filepath
        self.folder = os.path.dirname(filepath)


class FileDailyReportTest:
    filepath: str
    folder: str

    def __init__(self, filename: str):
        filepath = f"{os.path.abspath(__file__).split('/test')[0]}/test/data/SCAN/Reportes-Diarios/{filename}"
        self.filepath = filepath
        self.folder = os.path.dirname(filepath)

    def create_file(self) -> None:
        """Create a file with example data."""
        if os.path.isdir(f"{os.path.abspath(__file__).split('/test')[0]}/test/data"):
            shutil.rmtree(f"{os.path.abspath(__file__).split('/test')[0]}/test/data")
        os.makedirs(self.folder, exist_ok=True)
        date = datetime.now() - timedelta(days=1)
        date = date.strftime("%Y-%m-%d")
        with open(self.filepath, "w") as file:
            file.write("Interfaz Tipo Fecha Capacidad In Out In-Max Out-Max Uso-%\n")
            file.write(f"Interfaz-1 HUAWEI {date} 10 11617614 2296806 11890501 2323927 98\n")
            file.write(f"Interfaz-2 HUAWEI {date} 10 3515418 2152241 3605922 2243843 60\n")
            file.write(f"Interfaz-3 HUAWEI {date} 10 2824666 2263704 3462229 2338423 50\n")

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


class Database(ABC):
    uri: str
    name_db: str
    db_backup: bool

    def clean(self) -> None:
        """Clean all registers in the database."""
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"DELETE FROM {self.name_db}")
                database.commit()
                database.close()
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.name_db]
                collection.delete_many({})
                client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

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
        try:
            if os.path.exists(".env.test"): env = dotenv_values(".env.test")
            else: raise FileNotFoundError("No file `env.test` with environment variables found")
            uri_mongo = env.get("URI_MONGO")
            if uri_mongo: self.uri = uri_mongo
            else: raise Exception("Failed to obtain configuration. URI MongoDB variable not found in enviroment file")
            self.db_backup = db_backup
            self.name_db = "BORDE"
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def create_table(self) -> None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.name_db} (
                        {BordeFieldDatabase.ID} NUMERIC PRIMARY KEY,
                        {BordeFieldDatabase.NAME} VARCHAR(100) NOT NULL,
                        {BordeFieldDatabase.MODEL} VARCHAR(15) NOT NULL,
                        {BordeFieldDatabase.CAPACITY} SMALLINT NOT NULL,
                        {BordeFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE
                        CONSTRAINT {self.name_db}_unique UNIQUE ({BordeFieldDatabase.NAME}, {BordeFieldDatabase.MODEL})
                    )"""
                )
                database.commit()
                database.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def insert(self, data: BordeModel) -> None:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    INSERT INTO {self.name_db} (
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
                collection = database[self.name_db]
                collection.insert_one(data.model_dump())
                client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def get(self, id: int) -> list:
        try:
            if self.db_backup:
                database = psycopg2.connect(self.uri)
                cursor = database.cursor()
                cursor.execute(f"""
                    SELECT * 
                    FROM {self.name_db} 
                    WHERE {BordeFieldDatabase.ID} = %s""", (id,)
                )
                result = cursor.fetchone()
                database.close()
                return result
            else:
                client = MongoClient(self.uri)
                database = client[self.name_db]
                collection = database[self.name_db]
                result = collection.find_one({BordeFieldDatabase.ID: id})
                client.close()
                return result
        except Exception as e:
            traceback.print_exc(e)
            return []


if __name__ == "__main__":
    borde_example = BordeModel(id=None, name="INTERFACE_TEST_1", model="CISCO", capacity=10, createAt=datetime.now().strftime("%Y-%m-%d"))
    mongo = DatabaseBorderTest()
    mongo.create_table()
    mongo.insert(data=borde_example)
    response = mongo.get(id=1)
    print(response)
    mongo.clean()

    # postgres = DatabaseBorderTest(db_backup=True)
    # postgres.create_table()
    # postgres.insert(data=borde_example)
    # response = postgres.get(id=1)
    # postgres.clean()
    # mongo = DatabaseMongoTest()
    # inserted = mongo.insert(table="unittest", data={"name": "test"})
    # response = mongo.get(table="unittest", condition={"_id": inserted["_id"], "name": "test"})
    # mongo.clean(table="unittest")

    # postgres = DatabasePostgresTest()
    # postgres.create(table="unittest", query="(id SERIAL PRIMARY KEY, name VARCHAR(30) NOT NULL)")
    # inserted = postgres.insert(table="unittest", query="(name) VALUES ('test')")
    # response = postgres.get(name_collection="unittest", condition="name = 'test'")
    # postgres.clean(table="unittest")

    # filename_borde = f"{ModelBordeTypeTest.CISCO}%INTERFACE_TEST_1%10"
    # borde_data_example = FileBordeDataTest(filename_borde)
    # borde_data_example.create_file()
    # borde_data_example.delete_file()

    # filename_bras = f"{BrasTypeTest.UPLINK}%INTERFACE_TEST_1%10"
    # bras_data_example = FileBrasDataTest(filename_bras)
    # bras_data_example.create_file()
    # bras_data_example.delete_file()

    # filename_caching = f"SERVICIO%INTERFACE_TEST_1%22.5"
    # caching_data_example = FileCachingDataTest(filename_caching)
    # caching_data_example.create_file()
    # caching_data_example.delete_file()

    # filename_rai = f"DEDICADO%INTERFACE_TEST_1%0.04"
    # rai_data_example = FileRaiDataTest(filename_rai)
    # rai_data_example.create_file()
    # rai_data_example.delete_file()

    # FileDataTest.delete_father_folder()