import pandas as pd
from io import StringIO
from typing import List, Tuple
from database.constant.fields import (
    BordeFieldDatabase, 
    BrasFieldDatabase,
    CachingFieldDatabase,
    RaiFieldDatabase,
    TrafficHistoryFieldDatabase
)
from model import BordeModel, BrasModel, CachingModel, RaiModel, TrafficHistoryModel


class BordeResponseTrasform:
    """Class to transform response of databases."""

    @staticmethod
    def default_model_mongo(data: List[dict]) -> pd.DataFrame:
        """Transform response of mongo database.
        
        Parameters
        ----------
        data : List[dict]
            Data borde interfaces.
        """
        buffer: StringIO = StringIO()
        for interface in data:
            line = str(interface["_id"]) + ';'
            line += str(interface[BordeFieldDatabase.NAME]) + ';'
            line += str(interface[BordeFieldDatabase.MODEL]) + ';'
            line += str(interface[BordeFieldDatabase.CAPACITY]) + ';'
            line += str(interface[BordeFieldDatabase.CREATE_AT]) + '\n'
            buffer.write(line)
        buffer.seek(0)
        df = pd.read_csv(buffer, sep=';', header=None, names=[
            BordeFieldDatabase.ID,
            BordeFieldDatabase.NAME,
            BordeFieldDatabase.MODEL,
            BordeFieldDatabase.CAPACITY,
            BordeFieldDatabase.CREATE_AT
        ])
        return df
    
    @staticmethod
    def default_model_postgres(data: List[Tuple]) -> pd.DataFrame:
        """Transform response of postgres database.

        Parameters
        ----------
        data : List[Tuple]
            Data borde interfaces.
        """
        buffer: StringIO = StringIO()
        for interface in data:
            line = str(interface[0]) + ';'
            line += str(interface[1]) + ';'
            line += str(interface[2]) + ';'
            line += str(interface[3]) + ';'
            line += interface[4].strftime("%Y-%m-%d") + '\n'
            buffer.write(line)
        buffer.seek(0)
        df = pd.read_csv(buffer, sep=';', header=None, names=[
            BordeFieldDatabase.ID,
            BordeFieldDatabase.NAME,
            BordeFieldDatabase.MODEL,
            BordeFieldDatabase.CAPACITY,
            BordeFieldDatabase.CREATE_AT
        ])
        return df
    

class BrasResponseTrasform:
    """Class to transform response of databases."""

    @staticmethod
    def default_model_mongo(data: List[dict]) -> pd.DataFrame:
        """Transform response of mongo database.
        
        Parameters
        ----------
        data : List[dict]
            Data bras interfaces.
        """
        buffer: StringIO = StringIO()
        for interface in data:
            line = str(interface["_id"]) + ';'
            line += str(interface[BrasFieldDatabase.NAME]) + ';'
            line += str(interface[BrasFieldDatabase.TYPE]) + ';'
            line += str(interface[BrasFieldDatabase.CAPACITY]) + ';'
            line += str(interface[BrasFieldDatabase.CREATE_AT]) + '\n'
            buffer.write(line)
        buffer.seek(0)
        df = pd.read_csv(buffer, sep=';', header=None, names=[
            BrasFieldDatabase.ID,
            BrasFieldDatabase.NAME,
            BrasFieldDatabase.TYPE,
            BrasFieldDatabase.CAPACITY,
            BrasFieldDatabase.CREATE_AT
        ])
        return df
    
    @staticmethod
    def default_model_postgres(data: List[Tuple]) -> pd.DataFrame:
        """Transform response of postgres database.
        
        Parameters
        ----------
        data : List[Tuple]
            Data bras interfaces.
        """
        buffer: StringIO = StringIO()
        for interface in data:
            line = str(interface[0]) + ';'
            line += str(interface[1]) + ';'
            line += str(interface[2]) + ';'
            line += str(interface[3]) + ';'
            line += interface[4].strftime("%Y-%m-%d") + '\n'
            buffer.write(line)
        buffer.seek(0)
        df = pd.read_csv(buffer, sep=';', header=None, names=[
            RaiFieldDatabase.ID,
            RaiFieldDatabase.NAME,
            RaiFieldDatabase.CAPACITY,
            RaiFieldDatabase.CREATE_AT
        ])
        return df


class CachingResponseTrasform:
    """Class to transform response of databases."""

    @staticmethod
    def default_model_mongo(data: List[dict]) -> pd.DataFrame:
        """Transform response of mongo database.
        
        Parameters
        ----------
        data : List[dict]
            Data caching interfaces.
        """
        buffer: StringIO = StringIO()
        for interface in data:
            line = str(interface["_id"]) + ';'
            line += str(interface[CachingFieldDatabase.NAME]) + ';'
            line += str(interface[CachingFieldDatabase.SERVICE]) + ';'
            line += str(interface[CachingFieldDatabase.CAPACITY]) + ';'
            line += str(interface[CachingFieldDatabase.CREATE_AT]) + '\n'
            buffer.write(line)
        buffer.seek(0)
        df = pd.read_csv(buffer, sep=';', header=None, names=[
            CachingFieldDatabase.ID,
            CachingFieldDatabase.NAME,
            CachingFieldDatabase.SERVICE,
            CachingFieldDatabase.CAPACITY,
            CachingFieldDatabase.CREATE_AT
        ])
        return df
    
    @staticmethod
    def default_model_postgres(data: List[Tuple]) -> pd.DataFrame:
        """Transform response of postgres database.
        
        Parameters
        ----------
        data : List[Tuple]
            Data caching interfaces.
        """
        buffer: StringIO = StringIO()
        for interface in data:
            line = str(interface[0]) + ';'
            line += str(interface[1]) + ';'
            line += str(interface[2]) + ';'
            line += str(interface[3]) + ';'
            line += interface[4].strftime("%Y-%m-%d") + '\n'
            buffer.write(line)
        buffer.seek(0)
        df = pd.read_csv(buffer, sep=';', header=None, names=[
            CachingFieldDatabase.ID,
            CachingFieldDatabase.NAME,
            CachingFieldDatabase.SERVICE,
            CachingFieldDatabase.CAPACITY,
            CachingFieldDatabase.CREATE_AT
        ])
        return df
    

class RaiResponseTrasform:
    """Class to transform response of databases."""

    @staticmethod
    def default_model_mongo(data: List[dict]) -> pd.DataFrame:
        """Transform response of mongo database.
        
        Parameters
        ----------
        data : List[dict]
            Data rai interfaces.
        """
        buffer: StringIO = StringIO()
        for interface in data:
            line = str(interface["_id"]) + ';'
            line += str(interface[RaiFieldDatabase.NAME]) + ';'
            line += str(interface[RaiFieldDatabase.CAPACITY]) + ';'
            line += str(interface[RaiFieldDatabase.CREATE_AT]) + '\n'
            buffer.write(line)
        buffer.seek(0)
        df = pd.read_csv(buffer, sep=';', header=None, names=[
            RaiFieldDatabase.ID,
            RaiFieldDatabase.NAME,
            RaiFieldDatabase.CAPACITY,
            RaiFieldDatabase.CREATE_AT
        ])
        return df
    
    @staticmethod
    def default_model_postgres(data: List[Tuple]) -> pd.DataFrame:
        """Transform response of postgres database.
        
        Parameters
        ----------
        data : List[Tuple]
            Data rai interfaces.
        """
        buffer: StringIO = StringIO()
        for interface in data:
            line = str(interface[0]) + ';'
            line += str(interface[1]) + ';'
            line += str(interface[2]) + ';'
            line += interface[3].strftime("%Y-%m-%d") + '\n'
            buffer.write(line)
        buffer.seek(0)
        df = pd.read_csv(buffer, sep=';', header=None, names=[
            RaiFieldDatabase.ID,
            RaiFieldDatabase.NAME,
            RaiFieldDatabase.CAPACITY,
            RaiFieldDatabase.CREATE_AT
        ])
        return df


class TrafficHistoryResponseTrasform:
    """Class to transform response of databases."""

    @staticmethod
    def default_model_mongo(data: List[dict]) -> pd.DataFrame:
        """Transform response of mongo database.
        
        Parameters
        ----------
        data : List[dict]
            Data traffic history.
        """
        buffer: StringIO = StringIO()
        for interface in data:
            line = str(interface[TrafficHistoryFieldDatabase.DATE]) + ';'
            line += str(interface[TrafficHistoryFieldDatabase.TIME]) + ';'
            line += str(interface[TrafficHistoryFieldDatabase.ID_LAYER]) + ';'
            line += str(interface[TrafficHistoryFieldDatabase.TYPE_LAYER]) + ';'
            line += str(interface[TrafficHistoryFieldDatabase.IN_PROM]) + ';'
            line += str(interface[TrafficHistoryFieldDatabase.IN_MAX]) + ';'
            line += str(interface[TrafficHistoryFieldDatabase.OUT_PROM]) + ';'
            line += str(interface[TrafficHistoryFieldDatabase.OUT_MAX]) + '\n'
            buffer.write(line)
        buffer.seek(0)
        df = pd.read_csv(buffer, sep=';', header=None, names=[
            TrafficHistoryFieldDatabase.DATE,
            TrafficHistoryFieldDatabase.TIME,
            TrafficHistoryFieldDatabase.ID_LAYER,
            TrafficHistoryFieldDatabase.TYPE_LAYER,
            TrafficHistoryFieldDatabase.IN_PROM,
            TrafficHistoryFieldDatabase.IN_MAX,
            TrafficHistoryFieldDatabase.OUT_PROM,
            TrafficHistoryFieldDatabase.OUT_MAX
        ])
        return df
    
    @staticmethod
    def default_model_postgres(data: List[Tuple]) -> pd.DataFrame:
        """Transform response of postgres database.
        
        Parameters
        ----------
        data : List[Tuple]
            Data traffic history.
        """
        buffer: StringIO = StringIO()
        for interface in data:
            line = interface[0].strftime("%Y-%m-%d") + ';'
            line += interface[1].strftime("%H:%M:%S") + ';'
            line += str(interface[2]) + ';'
            line += str(interface[3]) + ';'
            line += str(interface[4]) + ';'
            line += str(interface[5]) + ';'
            line += str(interface[6]) + ';'
            line += str(interface[7]) + '\n'
            buffer.write(line)
        buffer.seek(0)
        df = pd.read_csv(buffer, sep=';', header=None, names=[
            TrafficHistoryFieldDatabase.DATE,
            TrafficHistoryFieldDatabase.TIME,
            TrafficHistoryFieldDatabase.ID_LAYER,
            TrafficHistoryFieldDatabase.TYPE_LAYER,
            TrafficHistoryFieldDatabase.IN_PROM,
            TrafficHistoryFieldDatabase.IN_MAX,
            TrafficHistoryFieldDatabase.OUT_PROM,
            TrafficHistoryFieldDatabase.OUT_MAX
        ])
        return df
