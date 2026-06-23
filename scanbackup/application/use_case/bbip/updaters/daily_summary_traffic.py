import json
import pandas as pd
from scanbackup.domain import (
    TrafficDailySummaryBBIPField,
    TrafficDailySummaryBBIPEntity,
    TrafficDailySummaryBBIPRepository,
)
from scanbackup.shared import TrafficDailySummaryBBIPHeader, SCANHeader

FACTOR_BBIP: float = 0.000000008022


class TrafficDailySummaryUpdaterUseCase:
    _repo: TrafficDailySummaryBBIPRepository

    def __init__(self, repo: TrafficDailySummaryBBIPRepository) -> None:
        self._repo = repo

    def execute(self, data: pd.DataFrame, sources: pd.DataFrame) -> None:
        data.columns = data.columns.str.lower()
        sources.columns = sources.columns.str.lower()

        summary = (
            data.groupby(
                [
                    SCANHeader.DATE.value.lower(),
                    SCANHeader.INTERFACE.value.lower(),
                    SCANHeader.LAYER.value.lower(),
                    SCANHeader.MODEL.value.lower(),
                ]
            )
            .agg(
                capacity=(SCANHeader.CAPACITY.value.lower(), "first"),
                in_prom=(SCANHeader.IN_PROM.value.lower(), "mean"),
                out_prom=(SCANHeader.OUT_PROM.value.lower(), "mean"),
                in_max=(SCANHeader.IN_MAX.value.lower(), "max"),
                out_max=(SCANHeader.OUT_MAX.value.lower(), "max"),
            )
            .reset_index()
        )

        summary[SCANHeader.IN_PROM.value.lower()] *= FACTOR_BBIP
        summary[SCANHeader.OUT_PROM.value.lower()] *= FACTOR_BBIP
        summary[SCANHeader.IN_MAX.value.lower()] *= FACTOR_BBIP
        summary[SCANHeader.OUT_MAX.value.lower()] *= FACTOR_BBIP

        summary[TrafficDailySummaryBBIPField.USE.value] = (
            summary[
                [SCANHeader.IN_MAX.value.lower(), SCANHeader.OUT_MAX.value.lower()]
            ].max(axis=1)
            / summary[SCANHeader.CAPACITY.value.lower()]
            * 100
        )

        merge_data = pd.merge(
            summary,
            sources,
            how="inner",
            on=[
                SCANHeader.INTERFACE.value.lower(),
                SCANHeader.LAYER.value.lower(),
                SCANHeader.MODEL.value.lower(),
            ],
            suffixes=("", "_y"),
        )

        merge_data = merge_data[
            [
                TrafficDailySummaryBBIPHeader.DATE.value.lower(),
                TrafficDailySummaryBBIPHeader.IN_PROM.value.lower(),
                TrafficDailySummaryBBIPHeader.IN_MAX.value.lower(),
                TrafficDailySummaryBBIPHeader.OUT_PROM.value.lower(),
                TrafficDailySummaryBBIPHeader.OUT_MAX.value.lower(),
                TrafficDailySummaryBBIPHeader.USE.value.lower(),
                TrafficDailySummaryBBIPHeader.DEVICE.value.lower(),
            ]
        ]

        data_json = merge_data.to_json(orient="records")

        records = json.loads(data_json)

        entities: list[TrafficDailySummaryBBIPEntity] = [
            TrafficDailySummaryBBIPEntity(**record) for record in records
        ]

        self._repo.insert(entities)
