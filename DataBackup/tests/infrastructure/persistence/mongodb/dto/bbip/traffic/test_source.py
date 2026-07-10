import unittest
from bson import ObjectId
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.traffic.source import (
    MongoTrafficSourceBBIPDTO,
)


class TestMongoTrafficSourceBBIPDTO(unittest.TestCase):
    """Unit tests for the MongoTrafficSourceBBIPDTO from_mongo mapping."""

    def test_from_mongo_maps_id_to_string(self) -> None:
        """from_mongo must convert the Mongo '_id' into the 'id' string field."""
        oid = ObjectId()
        doc = {
            "_id": oid,
            "link": "http://example.com",
            "interface": "Gi0/0/0",
            "capacity": 100.0,
            "type": "Cisco",
            "status": "ACTIVO",
            "layer": "BORDE",
            "comments": None,
        }

        dto = MongoTrafficSourceBBIPDTO.from_mongo(doc)

        self.assertEqual(dto.id, str(oid))
        self.assertEqual(dto.type, "Cisco")

    def test_comments_defaults_to_none(self) -> None:
        """Omitting comments must default to None instead of raising."""
        oid = ObjectId()
        doc = {
            "_id": oid,
            "link": "http://example.com",
            "interface": "Gi0/0/0",
            "capacity": 100.0,
            "type": "Cisco",
            "status": "ACTIVO",
            "layer": "BORDE",
        }

        dto = MongoTrafficSourceBBIPDTO.from_mongo(doc)

        self.assertIsNone(dto.comments)

    def test_id_defaults_to_none_when_omitted(self) -> None:
        """Building the DTO without an id (e.g. a projected-out '_id') must not fail."""
        dto = MongoTrafficSourceBBIPDTO(
            link="http://example.com",
            interface="Gi0/0/0",
            capacity=100.0,
            type="Cisco",
            status="ACTIVO",
            layer="BORDE",
        )
        self.assertIsNone(dto.id)


if __name__ == "__main__":
    unittest.main()
