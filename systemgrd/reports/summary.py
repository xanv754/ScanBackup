from pandas import DataFrame
from systemgrd.constants import LayerName, HeaderDailyReport
from systemgrd.handler import LayerHandler
from systemgrd.utils import calculate, ExcelExport, log


class SummaryReportBBIP:
    """Controller to manage summary data."""

    def _get_data_layers(
        self, df_data: DataFrame
    ) -> tuple[DataFrame, DataFrame, DataFrame, DataFrame, DataFrame]:
        df_borde = df_data[df_data[HeaderDailyReport.TYPE_LAYER] == LayerName.BORDE]
        df_borde = df_borde.drop(columns=[HeaderDailyReport.TYPE_LAYER])
        df_bras = df_data[df_data[HeaderDailyReport.TYPE_LAYER] == LayerName.BRAS]
        df_bras = df_bras.drop(columns=[HeaderDailyReport.TYPE_LAYER])
        df_caching = df_data[df_data[HeaderDailyReport.TYPE_LAYER] == LayerName.CACHING]
        df_caching = df_caching.drop(columns=[HeaderDailyReport.TYPE_LAYER])
        df_rai = df_data[df_data[HeaderDailyReport.TYPE_LAYER] == LayerName.RAI]
        df_rai = df_rai.drop(columns=[HeaderDailyReport.TYPE_LAYER])
        df_ixp = df_data[df_data[HeaderDailyReport.TYPE_LAYER] == LayerName.IXP]
        df_ixp = df_ixp.drop(columns=[HeaderDailyReport.TYPE_LAYER])
        return df_borde, df_bras, df_caching, df_rai, df_ixp

    def summary_diary(self, date: str | None = None, dev: bool = False) -> bool:
        try:
            handler = LayerHandler(dev=dev)
            df_data = handler.get_all_daily_report_by_date(date=date)
            df_borde, df_bras, df_caching, df_rai, df_ixp = self._get_data_layers(
                df_data=df_data
            )
            data = {
                LayerName.BORDE: df_borde,
                LayerName.BRAS: df_bras,
                LayerName.CACHING: df_caching,
                LayerName.RAI: df_rai,
                LayerName.IXP: df_ixp,
            }
            log.info("Resumen diario obtenido. Exportando...")
            excel = ExcelExport(filename="Resumen_Diario", data=data)
            excel.export(daily=True)
        except Exception as e:
            log.error(f"Failed to get summary report of diary. {e}")
            return False
        else:
            return True

    def summary_weekly(self, literal: bool = False, dev: bool = False) -> bool:
        try:
            handler = LayerHandler(dev=dev)
            if literal:
                df_data = handler.get_all_daily_data_by_days_before(day_before=8)
            else:
                df_data = handler.get_all_daily_data_on_week()
            df_borde, df_bras, df_caching, df_rai, df_ixp = self._get_data_layers(
                df_data=df_data
            )
            df_borde = calculate(df=df_borde)
            df_bras = calculate(df=df_bras)
            df_caching = calculate(df=df_caching)
            df_rai = calculate(df=df_rai)
            df_ixp = calculate(df=df_ixp)
            data = {
                LayerName.BORDE: df_borde,
                LayerName.BRAS: df_bras,
                LayerName.CACHING: df_caching,
                LayerName.RAI: df_rai,
                LayerName.IXP: df_ixp,
            }
            log.info("Resumen semanal obtenido. Exportando...")
            excel = ExcelExport(filename="Resumen_Semanal", data=data)
            excel.export()
        except Exception as e:
            log.error(f"Failed to get summary report of weekly. {e}")
            return False
        else:
            return True

    def summary_fortnight(self, literal: bool = False, dev: bool = False) -> bool:
        try:
            handler = LayerHandler(dev=dev)
            if literal:
                df_data = handler.get_all_daily_data_by_days_before(day_before=16)
            else:
                df_data = handler.get_all_daily_data_by_first_month(date_to=16)
            df_borde, df_bras, df_caching, df_rai, df_ixp = self._get_data_layers(
                df_data=df_data
            )
            df_borde = calculate(df=df_borde)
            df_bras = calculate(df=df_bras)
            df_caching = calculate(df=df_caching)
            df_rai = calculate(df=df_rai)
            df_ixp = calculate(df=df_ixp)
            data = {
                LayerName.BORDE: df_borde,
                LayerName.BRAS: df_bras,
                LayerName.CACHING: df_caching,
                LayerName.RAI: df_rai,
                LayerName.IXP: df_ixp,
            }
            log.info("Resumen quincenal obtenido. Exportando...")
            excel = ExcelExport(filename="Resumen_Quincenal", data=data)
            excel.export()
        except Exception as e:
            log.error(f"Failed to get summary report of fortnightly. {e}")
            return False
        else:
            return True

    def summary_monthly(self, literal: bool = False, dev: bool = False) -> bool:
        try:
            handler = LayerHandler(dev=dev)
            if literal:
                df_data = handler.get_all_daily_data_by_days_before(day_before=30)
            else:
                df_data = handler.get_all_daily_data_by_first_month()
            df_borde, df_bras, df_caching, df_rai, df_ixp = self._get_data_layers(
                df_data=df_data
            )
            df_borde = calculate(df=df_borde)
            df_bras = calculate(df=df_bras)
            df_caching = calculate(df=df_caching)
            df_rai = calculate(df=df_rai)
            df_ixp = calculate(df=df_ixp)
            data = {
                LayerName.BORDE: df_borde,
                LayerName.BRAS: df_bras,
                LayerName.CACHING: df_caching,
                LayerName.RAI: df_rai,
                LayerName.IXP: df_ixp,
            }
            log.info("Resumen mensual obtenido. Exportando...")
            excel = ExcelExport(filename="Resumen_Mensual", data=data)
            excel.export()
        except Exception as e:
            log.error(f"Failed to get summary report of monthly. {e}")
            return False
        else:
            return True
