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
                    new_columns.append("NOMBRE DE LA INTERFAZ")
                elif column == HeaderDataFrame.INTERFACE:
                    new_columns.append("INTERFAZ")
                elif (column == HeaderDataFrame.MODEL
                    or column == HeaderDataFrame.SERVICE
                    or column == HeaderDataFrame.TYPE
                ):
                    new_columns.append("TIPO")
                elif column == HeaderDataFrame.CAPACITY:
                    new_columns.append("CAPACIDAD")
                elif column == HeaderDataFrame.CREATE_AT:
                    new_columns.append("FECHA DE CREACIÓN")
                elif column == HeaderDataFrame.DATE:
                    new_columns.append("FECHA")
                elif column == HeaderDataFrame.TIME:
                    new_columns.append("HORA")
                elif column == HeaderDataFrame.ID_LAYER:
                    new_columns.append("ID DE LA INTERFAZ")
                elif column == HeaderDataFrame.TYPE_LAYER:
                    new_columns.append("CAPA")
                elif column == HeaderDataFrame.IN_PROM:
                    new_columns.append("IN PROM")
                elif column == HeaderDataFrame.OUT_PROM:
                    new_columns.append("OUT PROM")
                elif column == HeaderDataFrame.IN_MAX:
                    new_columns.append("IN MAX")
                elif column == HeaderDataFrame.OUT_MAX:
                    new_columns.append("OUT MAX")
                elif column == HeaderDataFrame.IN_MAX_PROM:
                    new_columns.append("IN MAX PROM")
                elif column == HeaderDataFrame.OUT_MAX_PROM:
                    new_columns.append("OUT MAX PROM")
                elif column == HeaderDataFrame.USE:
                    new_columns.append("USO (%)")
            df.columns = new_columns
        except Exception as error:
            log.error(f"Failed to translate header. {error}")
            return df
        else:
            return df