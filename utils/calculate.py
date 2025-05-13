import pandas as pd
from constants import HeaderDataFrame, header_summary
from utils import log


FACTOR = 0.000000008022

def calculate(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the traffic of a dataframe."""
    try:
        df_summary = pd.DataFrame(columns=header_summary)
        interfaces = df[HeaderDataFrame.NAME].unique()
        for interface in interfaces:
            df_filtered = df[df[HeaderDataFrame.NAME] == interface]
            in_prom = (df_filtered[HeaderDataFrame.IN_PROM].mean()) * FACTOR
            out_prom = (df_filtered[HeaderDataFrame.OUT_PROM].mean()) * FACTOR
            in_max_prom = (df_filtered[HeaderDataFrame.IN_MAX].max()) * FACTOR
            out_max_prom = (df_filtered[HeaderDataFrame.OUT_MAX].max()) * FACTOR
            if in_max_prom >= out_max_prom: use = (in_max_prom / df_filtered[HeaderDataFrame.CAPACITY][0]) * 100
            else: use = (out_max_prom / df_filtered[HeaderDataFrame.CAPACITY][0]) * 100
            new_df = pd.DataFrame([[interface, df_filtered[HeaderDataFrame.CAPACITY][0], in_prom, out_prom, in_max_prom, out_max_prom, use]], columns=header_summary)
            if df_summary.empty:
                df_summary = new_df
            else:
                df_summary = pd.concat([df_summary, new_df], axis=0, ignore_index=True)
        return df_summary
    except Exception as e:
        log.error(f"Failed to calculate traffic. {e}")
        return pd.DataFrame()