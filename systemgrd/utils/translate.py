import pandas as pd
from systemgrd.constants import HeaderBBIP, HeaderDailyReport, HeaderIPBras
from systemgrd.utils.log import log


class Translate:

    @staticmethod
    def header(df: pd.DataFrame) -> pd.DataFrame:
        """Translate header of dataframe."""
        try:
            columns = df.columns.to_list()
            new_columns = []
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
                elif column == HeaderBBIP.IN_VALUE:
                    new_columns.append("In")
                elif column == HeaderBBIP.OUT_VALUE:
                    new_columns.append("Out")
                elif column == HeaderBBIP.IN_MAX:
                    new_columns.append("In Max")
                elif column == HeaderBBIP.OUT_MAX:
                    new_columns.append("Out Max")
                elif column == HeaderDailyReport.IN_MAX:
                    new_columns.append("In Max Prom")
                elif column == HeaderDailyReport.OUT_MAX:
                    new_columns.append("Out Max Prom")
                elif column == HeaderDailyReport.IN_PROM:
                    new_columns.append("In Prom")
                elif column == HeaderDailyReport.OUT_PROM:
                    new_columns.append("Out Prom")
                elif column == HeaderDailyReport.USE:
                    new_columns.append("Uso (%)")
                elif column == HeaderIPBras.BRAS_NAME:
                    new_columns.append("Agregador")
            df.columns = new_columns
        except Exception as error:
            log.error(f"Failed to translate header. {error}")
            return df
        else:
            return df