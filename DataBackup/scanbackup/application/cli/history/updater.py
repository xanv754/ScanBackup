from datetime import date, timedelta
from scanbackup.infrastructure import (
    MongoTrafficHistoryBBIPRepository,
    MongoTrafficSourceBBIPRepository,
    MongoTrafficDailySummaryBBIPRepository,
)
from scanbackup.application.use_case.bbip.updaters.history_traffic import (
    TrafficHistoryUpdaterUseCase,
)
from scanbackup.domain import ValidatorConfig
from scanbackup.shared import LayerNotDefined


class TrafficHistoryUpdater:
    @staticmethod
    def execute(layer: str, date_str: str | None) -> None:
        if not date_str:
            yesterday = date.today() - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")

        if not ValidatorConfig.valid_layer_bbip(layer):
            raise LayerNotDefined(layer)

        layer = layer.upper()

        use_case = TrafficHistoryUpdaterUseCase(
            layer=layer,
            history_repository=MongoTrafficHistoryBBIPRepository(layer),
            source_repository=MongoTrafficSourceBBIPRepository(),
            daily_repository=MongoTrafficDailySummaryBBIPRepository(),
            data_date=date_str,
        )

        use_case.execute()
