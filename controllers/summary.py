from constants.group import LayerType
from handler import TrafficHandler
from utils.calculate import calculate


class SummaryController:
    """Controller to manage summary data."""

    @staticmethod
    def summary_diary_today() -> dict:
        """Get summary diary of today data.
        
        Returns
        -------
        dict
            Dict with key of layer type and value of dataframe.
        """
        traffic = TrafficHandler()
        df_data_borde = traffic.get_traffic_layer_by_days_before(layer_type=LayerType.BORDE, day_before=1)
        print(df_data_borde)
        # df_summary_borde = calculate(df_data_borde)
        # df_data_bras = traffic.get_traffic_layer_by_days_before(layer_type=LayerType.BRAS, day_before=1)
        # df_summary_bras = calculate(df_data_bras)
        # df_data_caching = traffic.get_traffic_layer_by_days_before(layer_type=LayerType.CACHING, day_before=1)
        # df_summary_caching = calculate(df_data_caching)
        # df_data_rai = traffic.get_traffic_layer_by_days_before(layer_type=LayerType.RAI, day_before=1)
        # df_summary_rai = calculate(df_data_rai)
        # data = {
        #     LayerType.BORDE: df_summary_borde,
        #     LayerType.BRAS: df_summary_bras,
        #     LayerType.CACHING: df_summary_caching,
        #     LayerType.RAI: df_summary_rai
        # }
        # return data


if __name__ == "__main__":
    SummaryController.summary_diary_today()