from enum import Enum
from pydantic import BaseModel, field_validator
from scanbackup.domain.validator import ValidatorConfig
from scanbackup.shared import SourceStatus, PyObjectId


class TrafficSourceBBIPField(str, Enum):
    LINK = "link"
    INTERFACE = "interface"
    CAPACITY = "capacity"
    MODEL = "model"
    STATUS = "status"
    LAYER = "layer"
    COMMENTS = "comments"


class TrafficSourceBBIPEntity(BaseModel):
    id: PyObjectId | None = None
    link: str
    interface: str
    capacity: float
    model: str
    layer: str
    status: str = SourceStatus.ACTIVE.value
    comments: str | None = None

    @field_validator("layer")
    @classmethod
    def layer_must_be_valid_bbip(cls, v):
        if not ValidatorConfig.valid_layer_bbip(v):
            raise ValueError(
                f"La capa '{v}' no está definida en la configuración del sistema"
            )
        return v
