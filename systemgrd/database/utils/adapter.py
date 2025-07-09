import pandas as pd
from io import StringIO
from typing import List
from systemgrd.constants import BBIPFieldName, DailyReportFieldName, header_bbip, header_daily_report
from systemgrd.utils import log


class BBIPResponseAdapter:
    """Class to transform BBIP layers response of databases."""

    @staticmethod
    def to_dataframe(data: List[dict]) -> pd.DataFrame:
        """Transform response of mongo database to dataframe.
        
        :param data: Data borde interfaces.
        :type data: List[dict]
        :return: Dataframe of borde interfaces.
        :rtype: pd.DataFrame
        """
        try:
            buffer: StringIO = StringIO()
            line: str = ""
            for interface in data:
                line += str(interface[BBIPFieldName.NAME]) + ';'
                line += str(interface[BBIPFieldName.TYPE]) + ';'
                line += str(interface[BBIPFieldName.CAPACITY]) + ';'
                line += str(interface[BBIPFieldName.DATE]) + ';'
                line += str(interface[BBIPFieldName.TIME]) + ';'
                line += str(interface[BBIPFieldName.IN_VALUE]) + ';'
                line += str(interface[BBIPFieldName.IN_MAX]) + ';'
                line += str(interface[BBIPFieldName.OUT_VALUE]) + ';'
                line += str(interface[BBIPFieldName.OUT_MAX]) + '\n'
                buffer.write(line)
            buffer.seek(0)
            df = pd.read_csv(buffer, sep=';', header=None, names=header_bbip)
            return df
        except Exception as error:
            log.error(f"Failed to BBIP response adapter. {error}")
            return pd.DataFrame(columns=header_bbip)
        

class DailyReportResponseAdapter:
    """Class to transform daily reports response of databases."""

    @staticmethod
    def to_dataframe(data: List[dict]) -> pd.DataFrame:
        """Transform response of mongo database to dataframe.
        
        :param data: Data borde interfaces.
        :type data: List[dict]
        :return: Dataframe of borde interfaces.
        :rtype: pd.DataFrame
        """
        try:
            buffer: StringIO = StringIO()
            line: str = ""
            for interface in data:
                line += str(interface[DailyReportFieldName.NAME]) + ';'
                line += str(interface[DailyReportFieldName.TYPE]) + ';'
                line += str(interface[DailyReportFieldName.CAPACITY]) + ';'
                line += str(interface[DailyReportFieldName.DATE]) + ';'
                line += str(interface[DailyReportFieldName.TYPE_LAYER]) + ';'
                line += str(interface[DailyReportFieldName.IN_PROM]) + ';'
                line += str(interface[DailyReportFieldName.OUT_PROM]) + ';'
                line += str(interface[DailyReportFieldName.IN_MAX]) + ';'
                line += str(interface[DailyReportFieldName.OUT_MAX]) + ';'
                line += str(interface[DailyReportFieldName.USE]) + '\n'
                buffer.write(line)
            buffer.seek(0)
            df = pd.read_csv(buffer, sep=';', header=None, names=header_daily_report)
            return df
        except Exception as error:
            log.error(f"Failed to BBIP response adapter. {error}")
            return pd.DataFrame(columns=header_daily_report)