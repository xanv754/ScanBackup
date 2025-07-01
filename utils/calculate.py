import pandas as pd
from constants import HeaderBBIP, HeaderDailyReport, header_daily_report
from utils.log import log


def calculate(df: pd.DataFrame, factor: int = 0.000000008022) -> pd.DataFrame:
    """Calculate the in and out prom and max prom with the use of a traffic dataframe."""
    try:
        summary_df = pd.DataFrame(columns=header_daily_report)
        interfaces = df[HeaderBBIP.NAME].unique()
        for interface in interfaces:
            df_filtered = df[df[HeaderBBIP.NAME] == interface]
            capacity = df_filtered[HeaderBBIP.CAPACITY].iloc[0]
            type = df_filtered[HeaderBBIP.TYPE].iloc[0]
            in_prom = (df_filtered[HeaderDailyReport.IN_PROM].mean()) * factor
            out_prom = (df_filtered[HeaderDailyReport.OUT_PROM].mean()) * factor
            in_max_prom = (float(df_filtered[HeaderDailyReport.IN_MAX].mean())) * factor
            out_max_prom = (float(df_filtered[HeaderDailyReport.OUT_MAX].mean())) * factor
            try:
                if in_max_prom >= out_max_prom:
                    use = (in_max_prom / capacity) * 100
                else:
                    use = (out_max_prom / capacity) * 100
            except ZeroDivisionError:
                use = 0
            df_final = pd.DataFrame({
                HeaderDailyReport.NAME: [interface],
                HeaderDailyReport.CAPACITY: [capacity],
                HeaderDailyReport.TYPE: [type],
                HeaderDailyReport.IN_PROM: [in_prom],
                HeaderDailyReport.OUT_PROM: [out_prom],
                HeaderDailyReport.IN_MAX_PROM: [in_max_prom],
                HeaderDailyReport.OUT_MAX_PROM: [out_max_prom],
                HeaderDailyReport.USE: [use]
            })
            if summary_df.empty: summary_df = df_final
            else: summary_df = pd.concat([summary_df, df_final], ignore_index=True)
        summary_df = summary_df.sort_values(by=HeaderDailyReport.NAME)
        summary_df.reset_index(drop=True, inplace=True)
        return summary_df
    except Exception as error:
        log.error(error)
        return pd.DataFrame(columns=header_daily_report)