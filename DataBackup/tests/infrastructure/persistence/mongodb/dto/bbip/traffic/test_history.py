import unittest
from datetime import date, time
from bson import ObjectId
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.traffic.history import (
    MongoTrafficHistoryBBIPDTO,
)


class TestMongoTrafficHistoryBBIPDTO(unittest.TestCase):
    """Unit tests for the MongoTrafficHistoryBBIPDTO from_mongo mapping."""

    def test_from_mongo_maps_id_to_string(self) -> None:
        """from_mongo must convert the Mongo '_id' into the 'id' string field."""
        oid = ObjectId()
        doc = {
            "_id": oid,
            "date": date(2026, 1, 1),
            "time": time(10, 0),
            "in_prom": 1.0,
            "in_max": 2.0,
            "out_prom": 1.5,
            "out_max": 2.5,
            "device": "Gi0/0/0",
        }

        dto = MongoTrafficHistoryBBIPDTO.from_mongo(doc)

        self.assertEqual(dto.id, str(oid))
        self.assertEqual(dto.out_max, 2.5)

    def test_id_defaults_to_none_when_omitted(self) -> None:
        """Building the DTO without an id (e.g. a projected-out '_id') must not fail."""
        dto = MongoTrafficHistoryBBIPDTO(
            date=date(2026, 1, 1),
            time=time(10, 0),
            in_prom=1.0,
            in_max=2.0,
            out_prom=1.5,
            out_max=2.5,
            device="Gi0/0/0",
        )
        self.assertIsNone(dto.id)


if __name__ == "__main__":
    unittest.main()
