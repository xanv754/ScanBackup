import pandas as pd
from constants.header import HeaderDataFrame, header_summary
from utils.log import log


def calculate(df: pd.DataFrame, factor: int = 0.000000008022) -> pd.DataFrame:
    """Calculate the in and out prom and max prom with the use of a traffic dataframe."""
    try:
        df_summary = pd.DataFrame(columns=header_summary)
        interfaces = df[HeaderDataFrame.INTERFACE].unique()
        for interface in interfaces:
            df_filtered = df[df[HeaderDataFrame.INTERFACE] == interface]
            type = df_filtered[HeaderDataFrame.TYPE].iloc[0]
            capacity = df_filtered[HeaderDataFrame.CAPACITY].iloc[0]
            in_prom = (df_filtered[HeaderDataFrame.IN_PROM].mean()) * factor
            out_prom = (df_filtered[HeaderDataFrame.OUT_PROM].mean()) * factor
            in_max_prom = (df_filtered[HeaderDataFrame.IN_MAX].max()) * factor
            out_max_prom = (df_filtered[HeaderDataFrame.OUT_MAX].max()) * factor
            if in_max_prom >= out_max_prom: use = (in_max_prom / capacity) * 100
            else: use = (out_max_prom / capacity) * 100
            new_df = pd.DataFrame([{
                HeaderDataFrame.INTERFACE: interface,
                HeaderDataFrame.TYPE: type,
                HeaderDataFrame.CAPACITY: capacity,
                HeaderDataFrame.IN_PROM: in_prom,
                HeaderDataFrame.OUT_PROM: out_prom,
                HeaderDataFrame.IN_MAX_PROM: in_max_prom,
                HeaderDataFrame.OUT_MAX_PROM: out_max_prom,
                HeaderDataFrame.USE: use
            }])
            if df_summary.empty: df_summary = new_df
            else: df_summary = pd.concat([df_summary, new_df], axis=0, ignore_index=True)
        return df_summary
    except Exception as e:
        log.error(f"Failed to calculate traffic. {e}")
        return pd.DataFrame()