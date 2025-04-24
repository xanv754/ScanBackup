from typing import List, Tuple
from model.boder import BordeModel
from model.bras import BrasModel
from model.caching import CachingModel
from model.rai import RaiModel
from model.trafficHistory import TrafficHistoryModel
from database.constant.fields import (
    BordeFieldDatabase, 
    BrasFieldDatabase,
    CachingFieldDatabase,
    RaiFieldDatabase,
    TrafficHistoryFieldDatabase
)


class BordeResponseTrasform:
    """Class to transform response of databases to borde model."""

    @staticmethod
    def default_model_mongo(data: List[dict]) -> List[BordeModel]:
        """Transform response of mongo database to borde model.
        
        Parameters
        ----------
        data : List[dict]
            Data borde interfaces.
        """
        data_transform: List[BordeModel] = []
        for interface in data:
            data_transform.append(
                BordeModel(
                    id=str(interface["_id"]),
                    name=interface[BordeFieldDatabase.NAME],
                    model=interface[BordeFieldDatabase.MODEL],
                    capacity=interface[BordeFieldDatabase.CAPACITY],
                    createAt=interface[BordeFieldDatabase.CREATE_AT]
                )
            )
        return data_transform
    
    @staticmethod
    def default_model_postgres(data: List[Tuple]) -> List[BordeModel]:
        """Transform response of postgres database to borde model.
        
        Parameters
        ----------
        data : List[Tuple]
            Data borde interfaces.
        """
        data_transform: List[BordeModel] = []
        for interface in data:
            data_transform.append(
                BordeModel(
                    id=str(interface[0]),
                    name=interface[1],
                    model=interface[2],
                    capacity=interface[3],
                    createAt=interface[4].strftime("%Y-%m-%d") 
                )
            )
        return data_transform
    

class BrasResponseTrasform:
    """Class to transform response of databases to bras model."""

    @staticmethod
    def default_model_mongo(data: List[dict]) -> List[BrasModel]:
        """Transform response of mongo database to bras model.
        
        Parameters
        ----------
        data : List[dict]
            Data bras interfaces.
        """
        data_transform: List[BrasModel] = []
        for interface in data:
            data_transform.append(
                BrasModel(
                    id=str(interface["_id"]),
                    name=interface[BrasFieldDatabase.NAME],
                    type=interface[BrasFieldDatabase.TYPE],
                    capacity=interface[BrasFieldDatabase.CAPACITY],
                    createAt=interface[BrasFieldDatabase.CREATE_AT]
                )
            )
        return data_transform
    
    @staticmethod
    def default_model_postgres(data: List[Tuple]) -> List[BrasModel]:
        """Transform response of postgres database to bras model.
        
        Parameters
        ----------
        data : List[Tuple]
            Data bras interfaces.
        """
        data_transform: List[BrasModel] = []
        for interface in data:
            data_transform.append(
                BrasModel(
                    id=str(interface[0]),
                    name=interface[1],
                    type=interface[2],
                    capacity=interface[3],
                    createAt=interface[4].strftime("%Y-%m-%d") 
                )
            )
        return data_transform


class CachingResponseTrasform:
    """Class to transform response of databases to caching model."""

    @staticmethod
    def default_model_mongo(data: List[dict]) -> List[CachingModel]:
        """Transform response of mongo database to caching model.
        
        Parameters
        ----------
        data : List[dict]
            Data caching interfaces.
        """
        data_transform: List[CachingModel] = []
        for interface in data:
            data_transform.append(
                CachingModel(
                    id=str(interface["_id"]),
                    name=interface[CachingFieldDatabase.NAME],
                    service=interface[CachingFieldDatabase.SERVICE],
                    capacity=interface[CachingFieldDatabase.CAPACITY],
                    createAt=interface[CachingFieldDatabase.CREATE_AT]
                )
            )
        return data_transform
    
    @staticmethod
    def default_model_postgres(data: List[Tuple]) -> List[CachingModel]:
        """Transform response of postgres database to caching model.
        
        Parameters
        ----------
        data : List[Tuple]
            Data caching interfaces.
        """
        data_transform: List[CachingModel] = []
        for interface in data:
            data_transform.append(
                CachingModel(
                    id=str(interface[0]),
                    name=interface[1],
                    service=interface[2],
                    capacity=interface[3],
                    createAt=interface[4].strftime("%Y-%m-%d") 
                )
            )
        return data_transform
    

class RaiResponseTrasform:
    """Class to transform response of databases to rai model."""

    @staticmethod
    def default_model_mongo(data: List[dict]) -> List[RaiModel]:
        """Transform response of mongo database to rai model.
        
        Parameters
        ----------
        data : List[dict]
            Data rai interfaces.
        """
        data_transform: List[RaiModel] = []
        for interface in data:
            data_transform.append(
                RaiModel(
                    id=str(interface["_id"]),
                    name=interface[RaiFieldDatabase.NAME],
                    capacity=interface[RaiFieldDatabase.CAPACITY],
                    createAt=interface[RaiFieldDatabase.CREATE_AT]
                )
            )
        return data_transform
    
    @staticmethod
    def default_model_postgres(data: List[Tuple]) -> List[RaiModel]:
        """Transform response of postgres database to rai model.
        
        Parameters
        ----------
        data : List[Tuple]
            Data rai interfaces.
        """
        data_transform: List[RaiModel] = []
        for interface in data:
            data_transform.append(
                RaiModel(
                    id=str(interface[0]),
                    name=interface[1],
                    capacity=interface[2],
                    createAt=interface[3].strftime("%Y-%m-%d") 
                )
            )
        return data_transform


class TrafficHistoryResponseTrasform:
    """Class to transform response of databases to traffic history model."""

    @staticmethod
    def default_model_mongo(data: List[dict]) -> List[TrafficHistoryModel]:
        """Transform response of mongo database to traffic history model.
        
        Parameters
        ----------
        data : List[dict]
            Data traffic history.
        """
        data_transform: List[TrafficHistoryModel] = []
        for interface in data:
            data_transform.append(
                TrafficHistoryModel(
                    date=interface[TrafficHistoryFieldDatabase.DATE],
                    time=interface[TrafficHistoryFieldDatabase.TIME],
                    idLayer=interface[TrafficHistoryFieldDatabase.ID_LAYER],
                    typeLayer=interface[TrafficHistoryFieldDatabase.TYPE_LAYER],
                    inProm=interface[TrafficHistoryFieldDatabase.IN_PROM],
                    inMax=interface[TrafficHistoryFieldDatabase.IN_MAX],
                    outProm=interface[TrafficHistoryFieldDatabase.OUT_PROM],
                    outMax=interface[TrafficHistoryFieldDatabase.OUT_MAX],
                )
            )
        return data_transform
    
    @staticmethod
    def default_model_postgres(data: List[Tuple]) -> List[TrafficHistoryModel]:
        """Transform response of postgres database to traffic history model.
        
        Parameters
        ----------
        data : List[Tuple]
            Data traffic history.
        """
        data_transform: List[TrafficHistoryModel] = []
        for interface in data:
            data_transform.append(
                TrafficHistoryModel(
                    date=interface[0].strftime("%Y-%m-%d"),
                    time=interface[1].strftime("%H:%M:%S"),
                    idLayer=str(interface[2]),
                    typeLayer=interface[3],
                    inProm=interface[4],
                    inMax=interface[5],
                    outProm=interface[6],
                    outMax=interface[7],
                )
            )
        return data_transform