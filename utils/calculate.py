import pandas as pd
from constants.header import HeaderTrafficDataFrameConstant
from utils.log import log


FACTOR = 0.000000008022

def calculate(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the traffic of a dataframe."""
    try:
        pass
    except Exception as e:
        log.error(f"Failed to calculate traffic. {e}")
        return pd.DataFrame()