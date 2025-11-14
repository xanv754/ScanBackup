import pandas as pd
from io import StringIO
from typing import List, Dict, Any
from pymongo.cursor import Cursor
from scanbackup.constants import (
    BBIPFieldName,
    IPBrasFieldName,
    DailySummaryFieldName,
    header_bbip,
    header_daily,
)
from scanbackup.utils import log


class BBIPResponseAdapter:
    """Class to transform BBIP layers response of databases."""

    @staticmethod
    def to_dataframe(data: List[Dict[Any, Any]] | Cursor[Any]) -> pd.DataFrame:
        """Transform response of mongo database to dataframe.

        :param data: Data borde interfaces.
        :type data: List[dict]
        :return DataFrame: Dataframe of borde interfaces.
        """
        try:
            buffer: StringIO = StringIO()
            line: str = ""
            for interface in data:
                line += str(interface[BBIPFieldName.NAME]) + ";"
                line += str(interface[BBIPFieldName.TYPE]) + ";"
                line += str(interface[BBIPFieldName.CAPACITY]) + ";"
                line += str(interface[BBIPFieldName.DATE]) + ";"
                line += str(interface[BBIPFieldName.TIME]) + ";"
                line += str(interface[BBIPFieldName.IN_PROM]) + ";"
                line += str(interface[BBIPFieldName.IN_MAX]) + ";"
                line += str(interface[BBIPFieldName.OUT_PROM]) + ";"
                line += str(interface[BBIPFieldName.OUT_MAX]) + "\n"
                buffer.write(line)
            buffer.seek(0)
            df = pd.read_csv(buffer, sep=";", header=None, names=header_bbip)
            return df
        except Exception as error:
            log.error(f"Fallo del adaptador para transformar la respuesta de la base de datos (BBIP) - {error}")
            return pd.DataFrame(columns=header_bbip)


class DailySummaryResponseAdapter:
    """Class to transform daily reports response of databases."""

    @staticmethod
    def to_dataframe(data: List[Dict[Any, Any]] | Cursor[Any]) -> pd.DataFrame:
        """Transform response of mongo database to dataframe.

        :param data: Data borde interfaces.
        :type data: List[dict]
        :return DataFrame: Dataframe of borde interfaces.
        """
        try:
            buffer: StringIO = StringIO()
            line: str = ""
            for interface in data:
                line += str(interface[DailySummaryFieldName.NAME]) + ";"
                line += str(interface[DailySummaryFieldName.TYPE]) + ";"
                line += str(interface[DailySummaryFieldName.CAPACITY]) + ";"
                line += str(interface[DailySummaryFieldName.DATE]) + ";"
                line += str(interface[DailySummaryFieldName.TYPE_LAYER]) + ";"
                line += str(interface[DailySummaryFieldName.IN_PROM]) + ";"
                line += str(interface[DailySummaryFieldName.OUT_PROM]) + ";"
                line += str(interface[DailySummaryFieldName.IN_MAX]) + ";"
                line += str(interface[DailySummaryFieldName.OUT_MAX]) + ";"
                line += str(interface[DailySummaryFieldName.USE]) + "\n"
                buffer.write(line)
            buffer.seek(0)
            df = pd.read_csv(buffer, sep=";", header=None, names=header_daily)
            return df
        except Exception as error:
            log.error(f"Fallo del adaptador para transformar la respuesta de la base de datos (reportes diarios) - {error}")
            return pd.DataFrame(columns=header_daily)


class IPBrasResponseAdapter:
    """Class to transform IPBras response of databases."""

    @staticmethod
    def to_dataframe(data: List[Dict[Any, Any]] | Cursor[Any]) -> pd.DataFrame:
        """Transform response of mongo database to dataframe.

        :param data: Data borde interfaces.
        :type data: List[dict]
        :return DataFrame: Dataframe of borde interfaces.
        """
        try:
            buffer: StringIO = StringIO()
            line: str = ""
            for interface in data:
                line += str(interface[IPBrasFieldName.DATE]) + ";"
                line += str(interface[IPBrasFieldName.TIME]) + ";"
                line += str(interface[IPBrasFieldName.IN_PROM]) + ";"
                line += str(interface[IPBrasFieldName.IN_MAX]) + ";"
                line += str(interface[IPBrasFieldName.BRAS_NAME]) + "\n"
                buffer.write(line)
            buffer.seek(0)
            df = pd.read_csv(buffer, sep=";", header=None, names=header_bbip)
            return df
        except Exception as error:
            log.error(f"Fallo del adaptador para transformar la respuesta de la base de datos (BBIP) - {error}")
            return pd.DataFrame(columns=header_bbip)