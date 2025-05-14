import pandas as pd
from constants.header import HeaderDataFrame, header_summary
from utils.log import log


def calculate(df: pd.DataFrame, factor: int = 0.000000008022) -> pd.DataFrame:
    """Calculate the in and out prom and max prom with the use of a traffic dataframe."""
    pass