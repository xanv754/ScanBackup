from calendar import monthrange
from datetime import datetime
from multiprocessing import Pool
from constants.group import LayerType
from handler import TrafficHandler, DailyReportHandler
from utils.calculate import calculate
from utils.translate import Translate
from utils.excel import ExcelExport


class SummaryController:
    """Controller to manage summary data."""

    @staticmethod
    def summary_diary_current() -> bool:
        """Get a summary of the current day's data."""
        try:
            daily_traffic = DailyReportHandler()
            with Pool(processes=4) as pool:
                df_data_borde = pool.apply(daily_traffic.get_daily_report_by_days_before, args=(LayerType.BORDE, 1))
                df_data_bras = pool.apply(daily_traffic.get_daily_report_by_days_before, args=(LayerType.BRAS, 1))
                df_data_caching = pool.apply(daily_traffic.get_daily_report_by_days_before, args=(LayerType.CACHING, 1))
                df_data_rai = pool.apply(daily_traffic.get_daily_report_by_days_before, args=(LayerType.RAI, 1))

                df_data_borde = Translate.header(df_data_borde)
                df_data_bras = Translate.header(df_data_bras)
                df_data_caching = Translate.header(df_data_caching)
                df_data_rai = Translate.header(df_data_rai)

                data = {
                    LayerType.BORDE: df_data_borde,
                    LayerType.BRAS: df_data_bras,
                    LayerType.CACHING: df_data_caching,
                    LayerType.RAI: df_data_rai
                }
            excel = ExcelExport(filename="Resumen_Diario", data=data)
            excel.export()
        except:
            return False
        else:
            return True

    @staticmethod
    def summary_weekly_current() -> bool:
        """Get a summary of the current weekly's data."""
        try:
            traffic = TrafficHandler()
            with Pool(processes=4) as pool:
                df_data_borde = pool.apply(traffic.get_traffic_layer_by_days_ago, args=(LayerType.BORDE, 7))
                df_data_bras = pool.apply(traffic.get_traffic_layer_by_days_ago, args=(LayerType.BRAS, 7))
                df_data_caching = pool.apply(traffic.get_traffic_layer_by_days_ago, args=(LayerType.CACHING, 7))
                df_data_rai = pool.apply(traffic.get_traffic_layer_by_days_ago, args=(LayerType.RAI, 7))

                df_data_borde = calculate(df_data_borde)
                df_data_bras = calculate(df_data_bras)
                df_data_caching = calculate(df_data_caching)
                df_data_rai = calculate(df_data_rai)

                df_data_borde = Translate.header(df_data_borde)
                df_data_bras = Translate.header(df_data_bras)
                df_data_caching = Translate.header(df_data_caching)
                df_data_rai = Translate.header(df_data_rai)

                data = {
                    LayerType.BORDE: df_data_borde,
                    LayerType.BRAS: df_data_bras,
                    LayerType.CACHING: df_data_caching,
                    LayerType.RAI: df_data_rai
                }
            excel = ExcelExport(filename="Resumen_Semanal", data=data)
            excel.export()
        except:
            return False
        else:
            return True
        
    @staticmethod
    def summary_fortnight_current() -> bool:
        """Get a summary of the current fortnight's data."""
        try:
            traffic = TrafficHandler()
            with Pool(processes=4) as pool:
                df_data_borde = pool.apply(traffic.get_traffic_layer_by_days_ago, args=(LayerType.BORDE, 15))
                df_data_bras = pool.apply(traffic.get_traffic_layer_by_days_ago, args=(LayerType.BRAS, 15))
                df_data_caching = pool.apply(traffic.get_traffic_layer_by_days_ago, args=(LayerType.CACHING, 15))
                df_data_rai = pool.apply(traffic.get_traffic_layer_by_days_ago, args=(LayerType.RAI, 15))

                df_data_borde = calculate(df_data_borde)
                df_data_bras = calculate(df_data_bras)
                df_data_caching = calculate(df_data_caching)
                df_data_rai = calculate(df_data_rai)

                df_data_borde = Translate.header(df_data_borde)
                df_data_bras = Translate.header(df_data_bras)
                df_data_caching = Translate.header(df_data_caching)
                df_data_rai = Translate.header(df_data_rai)

                data = {
                    LayerType.BORDE: df_data_borde,
                    LayerType.BRAS: df_data_bras,
                    LayerType.CACHING: df_data_caching,
                    LayerType.RAI: df_data_rai
                }
            excel = ExcelExport(filename="Resumen_Quincenal", data=data)
            excel.export()
        except:
            return False
        else:
            return True

    @staticmethod
    def summary_monthly_current() -> bool:
        """Get a summary of the current month's data."""
        try:
            current_year = datetime.now().year
            current_month = datetime.now().month
            days = monthrange(current_year, current_month)[1]
            traffic = TrafficHandler()
            with Pool(processes=4) as pool:
                df_data_borde = pool.apply(traffic.get_traffic_layer_by_days_ago, args=(LayerType.BORDE, days))
                df_data_bras = pool.apply(traffic.get_traffic_layer_by_days_ago, args=(LayerType.BRAS, days))
                df_data_caching = pool.apply(traffic.get_traffic_layer_by_days_ago, args=(LayerType.CACHING, days))
                df_data_rai = pool.apply(traffic.get_traffic_layer_by_days_ago, args=(LayerType.RAI, days))

                df_data_borde = calculate(df_data_borde)
                df_data_bras = calculate(df_data_bras)
                df_data_caching = calculate(df_data_caching)
                df_data_rai = calculate(df_data_rai)

                df_data_borde = Translate.header(df_data_borde)
                df_data_bras = Translate.header(df_data_bras)
                df_data_caching = Translate.header(df_data_caching)
                df_data_rai = Translate.header(df_data_rai)

                data = {
                    LayerType.BORDE: df_data_borde,
                    LayerType.BRAS: df_data_bras,
                    LayerType.CACHING: df_data_caching,
                    LayerType.RAI: df_data_rai
                }
            excel = ExcelExport(filename="Resumen_Mensual", data=data)
            excel.export()
        except:
            return False
        else:
            return True