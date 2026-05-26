from scanbackup.infrastructure.persistence.mongodb.dto.bbip.traffic.source import (
    BBIPTrafficSourceMongoDTO,
)
from scanbackup.domain.entities.bbip.traffic.source import BBIPTrafficSourceEntity


class BBIPTrafficSourceMapper:
    @staticmethod
    def to_entity(dto: BBIPTrafficSourceMongoDTO) -> BBIPTrafficSourceEntity:
        return BBIPTrafficSourceEntity(**dto.model_dump())
