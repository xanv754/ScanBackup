import pandas as pd
from constants.header import HeaderDataFrame
from utils.log import log


class Translate:

    @staticmethod
    def header(df: pd.DataFrame) -> pd.DataFrame:
        """Translate header of dataframe."""
        try:
            columns = df.columns.to_list()
            new_columns = []
            for column in columns:
                if column == HeaderDataFrame.ID:
                    new_columns.append("ID")
                elif column == HeaderDataFrame.NAME:
                    new_columns.append("Nombre de la Interfaz")
                elif column == HeaderDataFrame.INTERFACE:
                    new_columns.append("Interfaz")
                elif (column == HeaderDataFrame.MODEL
                    or column == HeaderDataFrame.SERVICE
                    or column == HeaderDataFrame.TYPE
                ):
                    new_columns.append("Tipo")
                elif column == HeaderDataFrame.CAPACITY:
                    new_columns.append("Capacidad")
                elif column == HeaderDataFrame.CREATE_AT:
                    new_columns.append("Fecha de Creación")
                elif column == HeaderDataFrame.DATE:
                    new_columns.append("Fecha")
                elif column == HeaderDataFrame.TIME:
                    new_columns.append("Hora")
                elif column == HeaderDataFrame.ID_LAYER:
                    new_columns.append("ID de la Interfaz")
                elif column == HeaderDataFrame.TYPE_LAYER:
                    new_columns.append("Capa")
                elif column == HeaderDataFrame.IN_PROM:
                    new_columns.append("In Prom")
                elif column == HeaderDataFrame.OUT_PROM:
                    new_columns.append("Out Prom")
                elif column == HeaderDataFrame.IN_MAX:
                    new_columns.append("In Max")
                elif column == HeaderDataFrame.OUT_MAX:
                    new_columns.append("Out Max")
                elif column == HeaderDataFrame.IN_MAX_PROM:
                    new_columns.append("In Max Prom")
                elif column == HeaderDataFrame.OUT_MAX_PROM:
                    new_columns.append("Out Max Prom")
                elif column == HeaderDataFrame.USE:
                    new_columns.append("Uso (%)")
            df.columns = new_columns
        except Exception as error:
            log.error(f"Failed to translate header. {error}")
            return df
        else:
            return df