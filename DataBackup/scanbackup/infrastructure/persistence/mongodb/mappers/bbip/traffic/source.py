from scanbackup.infrastructure.persistence.mongodb.dto.bbip.traffic.source import (
    MongoTrafficSourceBBIPDTO,
)
from scanbackup.domain.entities.bbip.traffic.source import TrafficSourceBBIPEntity


class TrafficSourceBBIPMapper:
    @staticmethod
    def to_entity(dto: MongoTrafficSourceBBIPDTO) -> TrafficSourceBBIPEntity:
        return TrafficSourceBBIPEntity(**dto.model_dump())
