import pandas as pd
from constants.header import HeaderDataFrame, header_summary
from utils.log import log


def calculate(df: pd.DataFrame, factor: int = 0.000000008022) -> pd.DataFrame:
    """Calculate the in and out prom and max prom with the use of a traffic dataframe."""
    try:
        print(df)
        summary_df = pd.DataFrame()
        interfaces = df[HeaderDataFrame.INTERFACE].unique()
        for interface in interfaces:
            df_filtered = df[df[HeaderDataFrame.INTERFACE] == interface]
            capacity = df_filtered[HeaderDataFrame.CAPACITY].iloc[0]
            type = df_filtered[HeaderDataFrame.TYPE].iloc[0]
            in_prom = (df_filtered[HeaderDataFrame.IN_PROM].mean()) * factor
            out_prom = (df_filtered[HeaderDataFrame.OUT_PROM].mean()) * factor
            in_max_prom = (float(df_filtered[HeaderDataFrame.IN_MAX].mean())) * factor
            out_max_prom = (float(df_filtered[HeaderDataFrame.OUT_MAX].mean())) * factor
            try:
                if in_max_prom >= out_max_prom:
                    use = (in_max_prom / capacity) * 100
                else:
                    use = (out_max_prom / capacity) * 100
            except ZeroDivisionError:
                use = 0
            df_final = pd.DataFrame({
                HeaderDataFrame.INTERFACE: [interface],
                HeaderDataFrame.CAPACITY: [capacity],
                HeaderDataFrame.TYPE: [type],
                HeaderDataFrame.IN_PROM: [in_prom],
                HeaderDataFrame.OUT_PROM: [out_prom],
                HeaderDataFrame.IN_MAX_PROM: [in_max_prom],
                HeaderDataFrame.OUT_MAX_PROM: [out_max_prom],
                HeaderDataFrame.USE: [use]
            })
            if summary_df.empty: summary_df = df_final
            else: summary_df = pd.concat([summary_df, df_final], ignore_index=True)
        summary_df = summary_df.sort_values(by=HeaderDataFrame.INTERFACE)
        summary_df.reset_index(drop=True, inplace=True)
        return summary_df
    except Exception as error:
        log.error(error)
        return pd.DataFrame(columns=header_summary)