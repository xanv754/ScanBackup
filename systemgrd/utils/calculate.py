import pandas as pd
from systemgrd.constants import HeaderBBIP, HeaderDailyReport, header_daily_report
from systemgrd.utils.log import log


def calculate(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the in and out prom and max prom with the use of a traffic dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Traffic dataframe.

    Returns
    -------
    pd.DataFrame
        Summary dataframe.
    """
    try:
        summary_df = pd.DataFrame(columns=header_daily_report)
        interfaces: list[str] = df[HeaderBBIP.NAME].unique()  # type: ignore
        for interface in interfaces:
            df_filtered: pd.DataFrame = df[df[HeaderBBIP.NAME] == interface]
            df_filtered = df_filtered.sort_values(
                by=[HeaderDailyReport.DATE], ascending=False
            )
            df_filtered = df_filtered.reset_index(drop=True)
            capacity = df_filtered[HeaderBBIP.CAPACITY].iloc[0]
            type = df_filtered[HeaderBBIP.TYPE].iloc[0]
            in_prom = df_filtered[HeaderDailyReport.IN_PROM].mean()
            out_prom = df_filtered[HeaderDailyReport.OUT_PROM].mean()
            in_max_prom = float(df_filtered[HeaderDailyReport.IN_MAX].mean())
            out_max_prom = float(df_filtered[HeaderDailyReport.OUT_MAX].mean())
            try:
                if in_max_prom >= out_max_prom:
                    use = (in_max_prom / capacity) * 100
                else:
                    use = (out_max_prom / capacity) * 100
            except ZeroDivisionError:
                use = 0
            df_final = pd.DataFrame(
                {
                    HeaderDailyReport.NAME: [interface],
                    HeaderDailyReport.CAPACITY: [capacity],
                    HeaderDailyReport.TYPE: [type],
                    HeaderDailyReport.IN_PROM: [in_prom],
                    HeaderDailyReport.OUT_PROM: [out_prom],
                    HeaderDailyReport.IN_MAX: [in_max_prom],
                    HeaderDailyReport.OUT_MAX: [out_max_prom],
                    HeaderDailyReport.USE: [use],
                }
            )
            if summary_df.empty:
                summary_df = df_final
            else:
                summary_df = pd.concat([summary_df, df_final], ignore_index=True)
        summary_df = summary_df.sort_values(by=HeaderDailyReport.NAME)
        summary_df.reset_index(drop=True, inplace=True)
        return summary_df
    except Exception as error:
        log.error(f"Error in calculate daily reports. {error}")
        return pd.DataFrame(columns=header_daily_report)
