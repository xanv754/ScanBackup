import os
import random
import traceback
from typing import List
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from dotenv import dotenv_values
from pymongo import MongoClient
from model import BBIPModel, IPBrasModel, DailyReportModel
from constants import (
    LayerName, TableName, 
    BBIPFieldName, IPBrasHistoryFieldName, DailyReportFieldName, 
)


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


class DatabaseBBIPTest(ABC):
    uri: str
    name_db: str
    table: str

    def __init__(self, table: str):
        try:
            if os.path.exists(".env.test"): env = dotenv_values(".env.test")
            else: raise FileNotFoundError("No file `env.test` with environment variables found")
            uri_mongo = env.get("URI_MONGO")
            if uri_mongo: self.uri = uri_mongo
            else: raise Exception("Failed to obtain configuration. URI MongoDB variable not found in enviroment file")
            name_db = self.uri.split("/")[-1]
            self.name_db = name_db
            self.table = table
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
        else:
            self.create_table()

    def clean(self, border: bool = False) -> None:
        """Clean all registers in the database."""
        try:
            client = MongoClient(self.uri)
            database = client[self.name_db]
            collection = database[self.table]
            collection.delete_many({})
            if border: 
                collection = database[LayerName.BORDE]
                collection.delete_many({})
            client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    @abstractmethod
    def get_exampĺe(self) -> BBIPModel:
        """Get an example of data."""
        pass

    def transform_model(self, data: list[dict]) -> List[BBIPModel]:
        """Transform data to model."""
        new_data: List[BBIPModel] = []
        for json in data:
            new_data.append(
                BBIPModel(
                    name=json[BBIPFieldName.NAME],
                    type=json[BBIPFieldName.TYPE],
                    capacity=json[BBIPFieldName.CAPACITY],
                    date=json[BBIPFieldName.DATE],
                    time=json[BBIPFieldName.TIME],
                    inProm=json[BBIPFieldName.IN_PROM],
                    inMax=json[BBIPFieldName.IN_MAX],
                    outProm=json[BBIPFieldName.OUT_PROM],
                    outMax=json[BBIPFieldName.OUT_MAX]
                )
            )
        return new_data

    def insert(self, data: BBIPModel) -> BBIPModel:
        """Insert a new register in the database."""
        try:
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

    def get(self, interface: str) -> list:
        """Get one registers from the database."""
        try:
            client = MongoClient(self.uri)
            database = client[self.name_db]
            collection = database[self.table]
            result = collection.find_one({ BBIPFieldName.NAME: interface })
            client.close()
            return self.transform_model([result])[0]
        except Exception as e:
            traceback.print_exc(e)
            return []

    def get_all(self) -> list[BBIPModel]:
        """Get all registers from the database."""
        try:
            client = MongoClient(self.uri)
            database = client[self.name_db]
            collection = database[self.table]
            result = collection.find()
            result = self.transform_model(result)
            client.close()
            return result
        except Exception as e:
            traceback.print_exc(e)
            return []


class DatabaseBorderTest(DatabaseBBIPTest):
    def __init__(self):
        super().__init__(table=TableName.BORDE)

    def get_exampĺe(self) -> BBIPModel:
        return BBIPModel(
            name=f"Interface_Test_{random.randint(1, 100)}",
            type=random.choice(["CISCO", "HUAWEI"]),
            capacity=random.randint(1, 100),
            date=datetime.now().strftime("%Y-%m-%d"),
            time=datetime.now().strftime("%H:%M:%S"),
            inProm=random.randint(1, 100),
            inMax=random.randint(1, 100),
            outProm=random.randint(1, 100),
            outMax=random.randint(1, 100)
        )

    def insert(self, data: BBIPModel | None = None) -> BBIPModel:
        if data is None: data = self.get_exampĺe()
        return super().insert(data=data)

    def get(self, interface: str) -> BBIPModel | None:
        return super().get(interface=interface)
        
    def get_all(self) -> list[BBIPModel]:
        return super().get_all()


class DatabaseBrasTest(DatabaseBBIPTest):
    def __init__(self):
        super().__init__(table=TableName.BRAS)

    def get_exampĺe(self) -> BBIPModel | None:
        return BBIPModel(
            name=f"Interface_Test_{random.randint(1, 100)}",
            type=random.choice(["UPLINK", "DOWNLINK"]),
            capacity=random.randint(1, 100),
            date=datetime.now().strftime("%Y-%m-%d"),
            time=datetime.now().strftime("%H:%M:%S"),
            inProm=random.randint(1, 100),
            inMax=random.randint(1, 100),
            outProm=random.randint(1, 100),
            outMax=random.randint(1, 100)
        )

    def insert(self, data: BBIPModel | None = None) -> BBIPModel:
        if data is None: data = self.get_exampĺe()
        return super().insert(data=data)

    def get(self, interface: str) -> BBIPModel | None:
        return super().get(interface=interface)
        
    def get_all(self) -> list[BBIPModel]:
        return super().get_all()


class DatabaseCachingTest(DatabaseBBIPTest):
    def __init__(self):
        super().__init__(table=TableName.CACHING)

    def get_exampĺe(self) -> BBIPModel | None:
        return BBIPModel(
            name=f"Interface_Test_{random.randint(1, 100)}",
            type=random.choice(["GOOGLE", "FACEBOOK", "AKAMAI", "ABATVGO"]),
            capacity=random.randint(1, 100),
            date=datetime.now().strftime("%Y-%m-%d"),
            time=datetime.now().strftime("%H:%M:%S"),
            inProm=random.randint(1, 100),
            inMax=random.randint(1, 100),
            outProm=random.randint(1, 100),
            outMax=random.randint(1, 100)
        )

    def insert(self, data: BBIPModel | None = None) -> BBIPModel:
        if data is None: data = self.get_exampĺe()
        return super().insert(data=data)

    def get(self, interface: str) -> BBIPModel | None:
        return super().get(interface=interface)
        
    def get_all(self) -> list[BBIPModel]:
        return super().get_all()
        

class DatabaseRaiTest(DatabaseBBIPTest):
    def __init__(self):
        super().__init__(table=TableName.RAI)

    def get_exampĺe(self) -> BBIPModel | None:
        return BBIPModel(
            name=f"Interface_Test_{random.randint(1, 100)}",
            type="DEDICADO",
            capacity=random.randint(1, 100),
            date=datetime.now().strftime("%Y-%m-%d"),
            time=datetime.now().strftime("%H:%M:%S"),
            inProm=random.randint(1, 100),
            inMax=random.randint(1, 100),
            outProm=random.randint(1, 100),
            outMax=random.randint(1, 100)
        )

    def insert(self, data: BBIPModel | None = None) -> BBIPModel:
        if data is None: data = self.get_exampĺe()
        return super().insert(data=data)

    def get(self, interface: str) -> BBIPModel | None:
        return super().get(interface=interface)
        
    def get_all(self) -> list[BBIPModel]:
        return super().get_all()


class DatabaseDailyTest(DatabaseBBIPTest):
    uri: str
    name_db: str
    table: str

    def __init__(self):
        try:
            if os.path.exists(".env.test"): env = dotenv_values(".env.test")
            else: raise FileNotFoundError("No file `env.test` with environment variables found")
            uri_mongo = env.get("URI_MONGO")
            if uri_mongo: self.uri = uri_mongo
            else: raise Exception("Failed to obtain configuration. URI MongoDB variable not found in enviroment file")
            name_db = self.uri.split("/")[-1]
            self.name_db = name_db
            self.table = TableName.DAILY_REPORT
        except Exception as e:
            traceback.print_exc(e)
            exit(1)
        else:
            self.create_table()

    def clean(self, border: bool = False) -> None:
        """Clean all registers in the database."""
        try:
            client = MongoClient(self.uri)
            database = client[self.name_db]
            collection = database[self.table]
            collection.delete_many({})
            if border: 
                collection = database[LayerName.BORDE]
                collection.delete_many({})
            client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    @abstractmethod
    def get_exampĺe(self) -> DailyReportModel:
        """Get an example of data."""
        return DailyReportModel(
            name=f"Interface_Test_{random.randint(1, 100)}",
            type=random.choice(["CISCO", "HUAWEI"]),
            capacity=random.randint(1, 100),
            date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            typeLayer=LayerName.BORDE,
            inProm=random.randint(1, 100),
            outProm=random.randint(1, 100),
            inMax=random.randint(1, 100),
            outMax=random.randint(1, 100),
            use=random.randint(1, 100)
        )

    def transform_model(self, data: list[dict]) -> List[DailyReportModel]:
        """Transform data to model."""
        new_data: List[DailyReportModel] = []
        for json in data:
            new_data.append(
                DailyReportModel(
                    name=json[DailyReportFieldName.NAME],
                    type=json[DailyReportFieldName.TYPE],
                    capacity=json[DailyReportFieldName.CAPACITY],
                    date=json[DailyReportFieldName.DATE],
                    inProm=json[DailyReportFieldName.IN_PROM],
                    inMax=json[DailyReportFieldName.IN_MAX],
                    outProm=json[DailyReportFieldName.OUT_PROM],
                    outMax=json[DailyReportFieldName.OUT_MAX]
                )
            )
        return new_data

    def insert(self, data: DailyReportModel) -> DailyReportModel:
        """Insert a new register in the database."""
        try:
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

    def get(self, interface: str) -> list:
        """Get one registers from the database."""
        try:
            client = MongoClient(self.uri)
            database = client[self.name_db]
            collection = database[self.table]
            result = collection.find_one({ DailyReportFieldName.NAME: interface })
            client.close()
            return self.transform_model([result])[0]
        except Exception as e:
            traceback.print_exc(e)
            return []

    def get_all(self) -> list[DailyReportModel]:
        """Get all registers from the database."""
        try:
            client = MongoClient(self.uri)
            database = client[self.name_db]
            collection = database[self.table]
            result = collection.find()
            result = self.transform_model(result)
            client.close()
            return result
        except Exception as e:
            traceback.print_exc(e)
            return []


if __name__ == "__main__":

    borde = DatabaseBorderTest()
    example = borde.insert()
    borde.get(interface=example.name)
    borde.clean()


    data_scan = FileBordeDataTest(filename="CISCO%INTERFACE_TEST_1%10")
    data_scan.create_file()
    data_scan.delete_file()

    data_daily_report = FileDailyReportTest(filename="Resumen_Borde.csv")
    data_daily_report.create_file()
    data_daily_report.delete_file()