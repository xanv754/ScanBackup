import unittest
from bson import ObjectId
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.ip.summaries import (
    MongoIPDailySummaryBBIPDTO,
)


class TestMongoIPDailySummaryBBIPDTO(unittest.TestCase):
    """Unit tests for the MongoIPDailySummaryBBIPDTO from_mongo mapping."""

    def test_from_mongo_maps_id_to_string(self) -> None:
        """from_mongo must convert the Mongo '_id' into the 'id' string field."""
        oid = ObjectId()
        doc = {"_id": oid, "in_prom": 1.0, "in_max": 2.0, "device": "Gi0/0/0"}

        dto = MongoIPDailySummaryBBIPDTO.from_mongo(doc)

        self.assertEqual(dto.id, str(oid))
        self.assertEqual(dto.in_max, 2.0)

    def test_id_defaults_to_none_when_omitted(self) -> None:
        """Building the DTO without an id (e.g. a projected-out '_id') must not fail."""
        dto = MongoIPDailySummaryBBIPDTO(in_prom=1.0, in_max=2.0, device="Gi0/0/0")
        self.assertIsNone(dto.id)


if __name__ == "__main__":
    unittest.main()
