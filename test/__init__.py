import os
import shutil
import random
import traceback
from typing import List
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from dotenv import dotenv_values
from pymongo import MongoClient
from database import (
    BORDE_SCHEMA_MONGO, BRAS_SCHEMA_MONGO,
    CACHING_SCHEMA_MONGO, RAI_SCHEMA_MONGO,
    IP_HISTORY_SCHEMA_MONGO, DAILY_REPORT_SCHEMA_MONGO
)
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
            shutil.rmtree(self.folder)

    @classmethod
    def delete_father_folder(cls) -> None:
        """Delete the father folder."""
        shutil.rmtree(f"{os.path.abspath(__file__).split('/test')[0]}/test/data")


class FileDataSCANTest(FileDataTest):

    def create_file(self) -> None:
        """Create a file with example data."""
        try:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
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
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            with open(self.filepath, "w") as file:
                file.write("Interfaz Tipo Capacidad Fecha In Out In-Max Out-Max Uso-%\n")
                file.write(f"Interfaz-1 HUAWEI 10 {date} 11617614 2296806 11890501 2323927 98\n")
                file.write(f"Interfaz-2 HUAWEI 10 {date} 3515418 2152241 3605922 2243843 60\n")
                file.write(f"Interfaz-3 HUAWEI 10 {date} 2824666 2263704 3462229 2338423 50\n")
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
            self.__start_db()
            self.table = table
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def __check_collection(self, name: str, client: MongoClient) -> bool:
        """Check if the collection exists."""
        collection_list = client.list_collection_names()
        return name in collection_list
    
    def __start_db(self) -> None:
        """Start the database."""
        try:
            client = MongoClient(self.uri)
            database = client[self.name_db]
            if not self.__check_collection(TableName.BORDE, database):
                database.create_collection(
                    TableName.BORDE,
                    validator=BORDE_SCHEMA_MONGO
                )
            if not self.__check_collection(TableName.BRAS, database):
                database.create_collection(
                    TableName.BRAS,
                    validator=BRAS_SCHEMA_MONGO
                )
            if not self.__check_collection(TableName.CACHING, database):
                database.create_collection(
                    TableName.CACHING,
                    validator=CACHING_SCHEMA_MONGO
                )
            if not self.__check_collection(TableName.RAI, database):
                database.create_collection(
                    TableName.RAI,
                    validator=RAI_SCHEMA_MONGO
                )
            if not self.__check_collection(TableName.IP_BRAS_HISTORY, database):
                database.create_collection(
                    TableName.IP_BRAS_HISTORY,
                    validator=IP_HISTORY_SCHEMA_MONGO
                )
            client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def clean(self) -> None:
        """Clean all registers in the database."""
        try:
            client = MongoClient(self.uri)
            database = client[self.name_db]
            collection = database[self.table]
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
                    inProm=json[BBIPFieldName.IN_VALUE],
                    inMax=json[BBIPFieldName.IN_MAX],
                    outProm=json[BBIPFieldName.OUT_VALUE],
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
            date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
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
            date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
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
            date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
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
            date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
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


class DatabaseDailyTest():
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
            self.__start_db()
            self.table = TableName.DAILY_REPORT
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def __check_collection(self, name: str, client: MongoClient) -> bool:
        """Check if the collection exists."""
        collection_list = client.list_collection_names()
        return name in collection_list
    
    def __start_db(self) -> None:
        """Start the database."""
        try:
            client = MongoClient(self.uri)
            database = client[self.name_db]
            if not self.__check_collection(TableName.DAILY_REPORT, database):
                database.create_collection(
                    TableName.DAILY_REPORT,
                    validator=DAILY_REPORT_SCHEMA_MONGO
                )
            client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def clean(self) -> None:
        """Clean all registers in the daily report collection."""
        try:
            client = MongoClient(self.uri)
            database = client[self.name_db]
            collection = database[TableName.DAILY_REPORT]
            collection.delete_many({})
            client.close()
        except Exception as e:
            traceback.print_exc(e)
            exit(1)

    def get_exampĺe(self, borde: bool = True, bras: bool = False, caching: bool = False, rai: bool = False) -> DailyReportModel:
        """Get an example of data."""
        if borde:
            typeLayer = LayerName.BORDE
            type = random.choice(["CISCO", "HUAWEI"])
        elif bras:
            typeLayer = LayerName.BRAS
            type = random.choice(["UPLINK", "DOWNLINK"])
        elif caching:
            typeLayer = LayerName.CACHING
            type = random.choice(["GOOGLE", "FACEBOOK", "AKAMAI", "ABATVGO"])
        elif rai:
            typeLayer = LayerName.RAI
            type = "DEDICADO"
        return DailyReportModel(
            name=f"Interface_Test_{random.randint(1, 100)}",
            type=type,
            capacity=random.randint(1, 100),
            date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            typeLayer=typeLayer,
            inProm=random.randint(1, 100),
            outProm=random.randint(1, 100),
            inMaxProm=random.randint(1, 100),
            outMaxProm=random.randint(1, 100),
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
                    typeLayer=json[DailyReportFieldName.TYPE_LAYER],
                    inProm=json[DailyReportFieldName.IN_PROM],
                    inMaxProm=json[DailyReportFieldName.IN_MAX],
                    outProm=json[DailyReportFieldName.OUT_PROM],
                    outMaxProm=json[DailyReportFieldName.OUT_MAX],
                    use=json[DailyReportFieldName.USE]
                )
            )
        return new_data

    def insert(self, data: DailyReportModel | None = None, borde: bool = False, bras: bool = False, caching: bool = False, rai: bool = False) -> DailyReportModel:
        """Insert a new register in the database."""
        try:
            if data is None: 
                if not borde and not bras and not caching and not rai: borde = True
                data = self.get_exampĺe(borde=borde, bras=bras, caching=caching, rai=rai)
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
    print(example)
    search = borde.get(interface=example.name)
    print(search)
    borde.clean()

    bras = DatabaseBrasTest()
    example = bras.insert()
    print(example)
    search = bras.get(interface=example.name)
    print(search)
    bras.clean()

    caching = DatabaseCachingTest()
    example = caching.insert()
    print(example)
    search = caching.get(interface=example.name)
    print(search)
    caching.clean()

    rai = DatabaseRaiTest()
    example = rai.insert()
    print(example)
    search = rai.get(interface=example.name)
    print(search)
    rai.clean()

    data_scan = FileBordeDataTest(filename="CISCO%INTERFACE_TEST_1%10")
    data_scan.create_file()
    data_scan.delete_file()
    data_scan.delete_father_folder()

    data_daily_report = FileDailyReportTest(filename="Resumen_Borde.csv")
    data_daily_report.create_file()
    data_daily_report.delete_file()
    data_daily_report.delete_father_folder()
