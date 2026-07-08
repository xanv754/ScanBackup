from bson import ObjectId
from typing import Any
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            lambda v: ObjectId(v) if not isinstance(v, ObjectId) else v,
            serialization=core_schema.to_string_ser_schema(),
        )
