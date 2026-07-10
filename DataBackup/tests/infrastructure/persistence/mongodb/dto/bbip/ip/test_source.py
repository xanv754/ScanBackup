import unittest
from bson import ObjectId
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.ip.source import (
    MongoIPSourceBBIPDTO,
)


class TestMongoIPSourceBBIPDTO(unittest.TestCase):
    """Unit tests for the MongoIPSourceBBIPDTO from_mongo mapping."""

    def test_from_mongo_maps_id_to_string(self) -> None:
        """from_mongo must convert the Mongo '_id' into the 'id' string field."""
        oid = ObjectId()
        doc = {
            "_id": oid,
            "link": "http://example.com",
            "device": "Gi0/0/0",
            "status": "ACTIVO",
            "layer": "DINT",
        }

        dto = MongoIPSourceBBIPDTO.from_mongo(doc)

        self.assertEqual(dto.id, str(oid))
        self.assertEqual(dto.layer, "DINT")

    def test_id_defaults_to_none_when_omitted(self) -> None:
        """Building the DTO without an id (e.g. a projected-out '_id') must not fail."""
        dto = MongoIPSourceBBIPDTO(
            link="http://example.com", device="Gi0/0/0", status="ACTIVO", layer="DINT"
        )
        self.assertIsNone(dto.id)


if __name__ == "__main__":
    unittest.main()
