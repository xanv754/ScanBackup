import os
import traceback
import psycopg2
from typing import List
from datetime import datetime
from abc import ABC, abstractmethod
from dotenv import dotenv_values
from pymongo import MongoClient
from database.constant.tables import TableNameDatabase as LayerTypeTest
from constants.group import ModelBordeType as ModelBordeTypeTest
from constants.path import PathConstant


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
            if os.path.exists(".env.development"): env = dotenv_values(".env.development")
            elif os.path.exists(".env.production"): env = dotenv_values(".env.production")
            elif os.path.exists(".env"): env = dotenv_values(".env")
            else: raise FileNotFoundError("No file with environment variables found")
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
    def __init__(self):
        try:
            if os.path.exists(".env.development"): env = dotenv_values(".env.development")
            elif os.path.exists(".env.production"): env = dotenv_values(".env.production")
            elif os.path.exists(".env"): env = dotenv_values(".env")
            else: raise FileNotFoundError("No file with environment variables found")
            uri_postgres = env.get("URI_POSTGRES")
            if uri_postgres: self.uri_postgres = uri_postgres
            else: raise Exception("Failed to obtain configuration. URI PostgreSQL variable not found in enviroment file")
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
        else:
            name_db = self.uri_postgres.split("/")[-1]
            self.name_db = name_db

    def create(self, table: str, fields: str) -> None:
        try:
            database = psycopg2.connect(self.uri_postgres)
            cursor = database.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({fields})")
            database.commit()
            database.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def clean(self, table: str) -> None:
        try:
            database = psycopg2.connect(self.uri_postgres)
            cursor = database.cursor()
            cursor.execute(f"DELETE FROM {table}")
            database.commit()
            database.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def insert(self, table: str, query: str) -> bool:
        try:
            database = psycopg2.connect(self.uri_postgres)
            cursor = database.cursor()
            cursor.execute(query)
            database.commit()
            status = cursor.statusmessage
            database.close()
            return status == "INSERT 0 1"
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def get(self, name_collection: str, condition: str) -> List[tuple]:
        try:
            database = psycopg2.connect(self.uri_postgres)
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
        pass

    def delete_file(self) -> None:
        """Delete the example file."""
        pass


class FileBordeDataTest(FileDataTest):
    def __init__(self, filename: str):
        filepath = f"{os.path.realpath("./")}/test/data/SCAN/Borde/{filename}"
        self.filepath = filepath
        self.folder = os.path.dirname(filepath)


    def create_file(self) -> None:
        """Create a file with example data."""
        os.makedirs(self.folder, exist_ok=True)
        with open(self.filepath, "w") as file:
            file.write("Fecha Hora InPro OutPro InMax OutMax\n")
            file.write(f"{datetime.now().strftime("%Y-%m-%d")} 17:35:00 11617614 2296806 11890501 2323927\n")
            file.write(f"{datetime.now().strftime("%Y-%m-%d")} 20:55:00 3515418 2152241 3605922 2243843\n")
            file.write(f"{datetime.now().strftime("%Y-%m-%d")} 23:50:00 2824666 2263704 3462229 2338423\n")
    
    def delete_file(self) -> None:
        """Delete the example file."""
        if os.path.isfile(self.filepath):
            os.remove(self.filepath)
            if os.path.isdir(self.folder):
                os.rmdir(self.folder)


if __name__ == "__main__":
    mongo = DatabaseMongoTest()
    inserted = mongo.insert(table="unittest", data={"name": "test"})
    response = mongo.get(table="unittest", condition={"_id": inserted["_id"], "name": "test"})
    mongo.clean(table="unittest")

    postgres = DatabasePostgresTest()
    postgres.create(table="unittest", fields="id SERIAL PRIMARY KEY, name VARCHAR(30) NOT NULL")
    inserted = postgres.insert(table="unittest", query="INSERT INTO unittest (name) VALUES ('test')")
    response = postgres.get(name_collection="unittest", condition="name = 'test'")
    postgres.clean(table="unittest")

    filename = f"{ModelBordeTypeTest.CISCO}%INTERFACE_TEST_1%10"
    borde_data_example = FileBordeDataTest(filename)
    borde_data_example.create_file()
    borde_data_example.delete_file()
