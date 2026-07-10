import unittest
from unittest.mock import patch
from scanbackup.infrastructure.persistence.mongodb.mappers.bbip.traffic.source import (
    TrafficSourceBBIPMapper,
)
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.traffic.source import (
    MongoTrafficSourceBBIPDTO,
)


class TestTrafficSourceBBIPMapper(unittest.TestCase):
    """Unit tests for the TrafficSourceBBIPMapper.to_entity conversion."""

    @patch("scanbackup.domain.services.validator.ValidatorConfig.valid_layer_bbip")
    def test_maps_dto_type_to_entity_model(self, mock_valid_layer) -> None:
        """The DTO's 'type' field must be mapped to the entity's 'model' field."""
        mock_valid_layer.return_value = True
        dto = MongoTrafficSourceBBIPDTO(
            id="abc123",
            link="http://example.com",
            interface="Gi0/0/0",
            capacity=100.0,
            type="Cisco",
            status="ACTIVO",
            layer="BORDE",
        )

        entity = TrafficSourceBBIPMapper.to_entity(dto)

        self.assertEqual(entity.model, "Cisco")
        self.assertEqual(entity.interface, "Gi0/0/0")


if __name__ == "__main__":
    unittest.main()
