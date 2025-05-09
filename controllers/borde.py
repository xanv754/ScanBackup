from datetime import datetime
from constants.group import LayerType
from handler.traffic import TrafficHandler


class BordeController:
    """Controller to manage borde data."""

    @staticmethod
    def summary_diary(date: str = datetime.now().strftime("%Y-%m-%d")) -> dict:
        """Get summary diary of borde data."""
        traffic = TrafficHandler()
        data = traffic.get_traffic_layer_by_thirty_days_before(layer_type=LayerType.BORDE, date=date)
        print(data)


if __name__ == "__main__":
    BordeController.summary_diary(date="2025-05-08")