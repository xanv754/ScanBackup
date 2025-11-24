from pandas import DataFrame
from scanbackup.constants import LayerName, HeaderDailySummary
from scanbackup.handler import LayerHandler
from scanbackup.utils import calculate, ExcelExport, log


class SummaryReportBBIP:
    """Controller to manage summary data."""

    def _get_data_layers(
        self, df_data: DataFrame
    ) -> tuple[DataFrame, DataFrame, DataFrame, DataFrame, DataFrame]:
        """Splits all data by layers.

        :return DataFrame: Data separated by layer: Edge, Bras, Caching, Rai, Ixp
        """
        df_borde = df_data[df_data[HeaderDailySummary.TYPE_LAYER] == LayerName.BORDE]
        df_borde = df_borde.drop(columns=[HeaderDailySummary.TYPE_LAYER])
        df_bras = df_data[df_data[HeaderDailySummary.TYPE_LAYER] == LayerName.BRAS]
        df_bras = df_bras.drop(columns=[HeaderDailySummary.TYPE_LAYER])
        df_caching = df_data[df_data[HeaderDailySummary.TYPE_LAYER] == LayerName.CACHING]
        df_caching = df_caching.drop(columns=[HeaderDailySummary.TYPE_LAYER])
        df_rai = df_data[df_data[HeaderDailySummary.TYPE_LAYER] == LayerName.RAI]
        df_rai = df_rai.drop(columns=[HeaderDailySummary.TYPE_LAYER])
        df_ixp = df_data[df_data[HeaderDailySummary.TYPE_LAYER] == LayerName.IXP]
        df_ixp = df_ixp.drop(columns=[HeaderDailySummary.TYPE_LAYER])
        return df_borde, df_bras, df_caching, df_rai, df_ixp

    def summary_diary(self, date: str | None = None, default: bool = False, dev: bool = False) -> bool:
        """Gets all layer data required for the daily report.

        :param date: Date to get data.
        :type date: str | None
        :param dev: If True, get data from development environment.
        :type dev: bool
        :param default: If True, get data in the same format as you received it.
        :type default: bool
        :returns bool: True if the data was successfully retrieved, False otherwise.
        """
        try:
            handler = LayerHandler(dev=dev)
            df_data = handler.get_all_daily_summary_by_date(date=date)
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
            log.info("Data del reporte diario de BBIP obtenido. Exportando...")
            if not default:
                excel = ExcelExport(filename="Data_Diario_BBIP", data=data)
                excel.export(daily=True)
            else:
                pass
        except Exception as error:
            log.error(f"Summary report. Fallo al obtener el reporte diario del BBIP - {error}")
            return False
        else:
            return True

    def summary_weekly(self, literal: bool = False, dev: bool = False) -> bool:
        """Gets all layer data for the weekly report.

        :return Dict: Dictionary with data separated by layers.
        """
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
            log.info("Data del reporte semanal del BBIP obtenido. Exportando...")
            excel = ExcelExport(filename="Data_Semanal_BBIP", data=data)
            excel.export()
        except Exception as error:
            log.error(f"Summary report. Fallo al obtener el reporte semanal del BBIP - {error}")
            return False
        else:
            return True

    def summary_fortnight(self, literal: bool = False, dev: bool = False) -> bool:
        """Gets all layer data required for the biweekly report.

        :return Dict: Dictionary with data segmented by layers.
        """
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
            log.info("Data del reporte quincenal del BBIP obtenido. Exportando...")
            excel = ExcelExport(filename="Data_Quincenal_BBIP", data=data)
            excel.export()
        except Exception as error:
            log.error(f"Summary report. Fallo al obtener el reporte quincenal del BBIP - {error}")
            return False
        else:
            return True

    def summary_monthly(self, literal: bool = False, dev: bool = False) -> bool:
        """Gets all layer data required for the monthly report.

        :return Dict: Dictionary with data segmented by layers.
        """
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
            log.info("Data del reporte mensual del BBIP obtenido. Exportando...")
            excel = ExcelExport(filename="Data_Mensual_BBIP", data=data)
            excel.export()
        except Exception as error:
            log.error(f"Summary report. Fallo al obtener el reporte mensual del BBIP - {error}")
            return False
        else:
            return True
