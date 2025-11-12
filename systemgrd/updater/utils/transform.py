import pandas as pd
from systemgrd.constants import header_source
from systemgrd.model import Source
from systemgrd.utils import log


class TransForm:
    @staticmethod
    def model_to_df(models: list[Source]) -> pd.DataFrame:
        """Transform the list of models to a dataframe.

        :param models: The list of models to transform.
        :type models: list[Source]
        :returns DataFrame: DataFrame of model data.
        """
        try:
            json = [interface.model_dump() for interface in models]
            df = pd.DataFrame(json)
            return df
        except Exception as error:
            log.error(f"Fallo al transformar la lista de modelos a un dataframe - {error}")
            return pd.DataFrame(columns=header_source)