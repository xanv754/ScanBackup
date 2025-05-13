from constants.group import LayerType
from handler import TrafficHandler
from utils import calculate


class BordeController:
    """Controller to manage borde data."""

    @staticmethod
    def summary_diary_today() -> dict:
        """Get summary diary of borde data."""
        traffic = TrafficHandler()
        data = traffic.get_traffic_layer_by_days_before(layer_type=LayerType.BORDE, day_before=1)
        print(data)
        # df_summary = calculate(data)
        # print(df_summary)


if __name__ == "__main__":
    BordeController.summary_diary_today()