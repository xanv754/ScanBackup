from scanbackup.infrastructure.persistence.mongodb.dto.bbip.traffic.source import (
    MongoTrafficSourceBBIPDTO,
)
from scanbackup.domain.entities.bbip.traffic.source import BBIPTrafficSourceEntity


class TrafficSourceBBIPMapper:
    @staticmethod
    def to_entity(dto: MongoTrafficSourceBBIPDTO) -> BBIPTrafficSourceEntity:
        return BBIPTrafficSourceEntity(**dto.model_dump())
