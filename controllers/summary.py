from calendar import monthrange
from datetime import datetime
from multiprocessing import Pool
from constants.group import LayerType
from handler import TrafficHandler
from utils.calculate import calculate


class SummaryController:
    """Controller to manage summary data."""

    @staticmethod
    def summary_diary_current() -> dict:
        """Get a summary of the current day's data."""
        traffic = TrafficHandler()
        with Pool(processes=4) as pool:
            df_data_borde = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.BORDE, 1))
            df_data_bras = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.BRAS, 1))
            df_data_caching = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.CACHING, 1))
            df_data_rai = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.RAI, 1))


    @staticmethod
    def summary_weekly_current() -> dict:
        """Get a summary of the current weekly's data."""
        traffic = TrafficHandler()
        with Pool(processes=4) as pool:
            df_data_borde = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.BORDE, 7))
            df_data_bras = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.BRAS, 7))
            df_data_caching = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.CACHING, 7))
            df_data_rai = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.RAI, 7))

    @staticmethod
    def summary_fortnight_current() -> dict:
        """Get a summary of the current fortnight's data."""
        traffic = TrafficHandler()
        with Pool(processes=4) as pool:
            df_data_borde = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.BORDE, 15))
            df_data_bras = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.BRAS, 15))
            df_data_caching = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.CACHING, 15))
            df_data_rai = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.RAI, 15))

    @staticmethod
    def summary_monthly_current() -> dict:
        """Get a summary of the current month's data."""
        current_year = datetime.now().year
        current_month = datetime.now().month
        days = monthrange(current_year, current_month)[1]
        traffic = TrafficHandler()
        with Pool(processes=4) as pool:
            df_data_borde = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.BORDE, days))
            df_data_bras = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.BRAS, days))
            df_data_caching = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.CACHING, days))
            df_data_rai = pool.apply(traffic.get_traffic_layer_by_days_before, args=(LayerType.RAI, days))

            # df_summary_rai = calculate(df_data_rai)


if __name__ == "__main__":
    SummaryController.summary_diary_current()