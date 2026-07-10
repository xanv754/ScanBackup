import unittest
from bson import ObjectId
from pydantic import BaseModel
from scanbackup.shared.types.pyobjectid import PyObjectId


class _Wrapper(BaseModel):
    """Minimal pydantic model to exercise PyObjectId validation."""

    model_config = {"arbitrary_types_allowed": True}
    device: PyObjectId


class TestPyObjectId(unittest.TestCase):
    """Unit tests for the PyObjectId pydantic-compatible type."""

    def test_accepts_an_existing_objectid(self) -> None:
        """An existing ObjectId instance must be kept as-is."""
        oid = ObjectId()
        wrapper = _Wrapper(device=oid)
        self.assertEqual(wrapper.device, oid)

    def test_accepts_a_valid_hex_string(self) -> None:
        """A valid 24-char hex string must be converted into an ObjectId."""
        hex_id = str(ObjectId())
        wrapper = _Wrapper(device=hex_id)
        self.assertIsInstance(wrapper.device, ObjectId)
        self.assertEqual(str(wrapper.device), hex_id)

    def test_serializes_to_string(self) -> None:
        """Dumping the model to JSON must serialize the ObjectId as a string."""
        oid = ObjectId()
        wrapper = _Wrapper(device=oid)
        dumped = wrapper.model_dump(mode="json")
        self.assertEqual(dumped["device"], str(oid))

    def test_rejects_invalid_value(self) -> None:
        """An invalid identifier must raise an error when building the model."""
        with self.assertRaises(Exception):
            _Wrapper(device="not-a-valid-object-id")


if __name__ == "__main__":
    unittest.main()
