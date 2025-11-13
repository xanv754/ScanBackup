import pandas as pd
from scanbackup.constants import HeaderBBIP, HeaderDailySummary, HeaderIPBras
from scanbackup.utils.configuration.log import log


class TransformData:

    @staticmethod
    def translate_header(df: pd.DataFrame) -> pd.DataFrame:
        """Translate header of dataframe."""
        try:
            columns = df.columns.to_list()
            new_columns: list[str] = []
            for column in columns:
                if column == HeaderBBIP.NAME:
                    new_columns.append("Interfaz")
                elif column == HeaderBBIP.TYPE:
                    new_columns.append("Tipo")
                elif column == HeaderBBIP.CAPACITY:
                    new_columns.append("Capacidad")
                elif column == HeaderBBIP.DATE:
                    new_columns.append("Fecha")
                elif column == HeaderBBIP.TIME:
                    new_columns.append("Hora")
                elif column == HeaderBBIP.TYPE_LAYER:
                    new_columns.append("Capa")
                elif column == HeaderBBIP.IN_PROM:
                    new_columns.append("In")
                elif column == HeaderBBIP.OUT_PROM:
                    new_columns.append("Out")
                elif column == HeaderBBIP.IN_MAX:
                    new_columns.append("In Max")
                elif column == HeaderBBIP.OUT_MAX:
                    new_columns.append("Out Max")
                elif column == HeaderDailySummary.IN_MAX:
                    new_columns.append("In Max Prom")
                elif column == HeaderDailySummary.OUT_MAX:
                    new_columns.append("Out Max Prom")
                elif column == HeaderDailySummary.IN_PROM:
                    new_columns.append("In Prom")
                elif column == HeaderDailySummary.OUT_PROM:
                    new_columns.append("Out Prom")
                elif column == HeaderDailySummary.USE:
                    new_columns.append("Uso (%)")
                elif column == HeaderIPBras.BRAS_NAME:
                    new_columns.append("Agregador")
            df.columns = new_columns
        except Exception as error:
            log.error(f"Fallo al traducir los encabezados del reporte - {error}")
            return df
        else:
            return df

    @staticmethod
    def reorganize(df: pd.DataFrame) -> pd.DataFrame:
        """Reorganizes the columns of data for the report.

        :param df: Data to organize.
        :type df: DataFrame
        :return DataFrame: Organized data.
        """
        try:
            header_reports = [
                HeaderDailySummary.NAME,
                HeaderDailySummary.IN_PROM,
                HeaderDailySummary.IN_MAX,
                HeaderDailySummary.OUT_PROM,
                HeaderDailySummary.OUT_MAX,
                HeaderDailySummary.CAPACITY,
                HeaderDailySummary.TYPE,
                HeaderDailySummary.USE,
            ]
            if set(df.columns.to_list()) == set(header_reports):
                df = df[
                    [
                        HeaderDailySummary.NAME,
                        HeaderDailySummary.IN_PROM,
                        HeaderDailySummary.IN_MAX,
                        HeaderDailySummary.OUT_PROM,
                        HeaderDailySummary.OUT_MAX,
                        HeaderDailySummary.CAPACITY,
                        HeaderDailySummary.TYPE,
                        HeaderDailySummary.USE,
                    ]
                ]
            return df
        except Exception as error:
            log.error(f"Fallo al reorganizar las columnas del reporte - {error}")
            return df
