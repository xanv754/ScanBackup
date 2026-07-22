from enum import Enum
from pydantic import BaseModel, field_validator
from scanbackup.domain.validator import ValidatorConfig
from scanbackup.shared import SourceStatus, PyObjectId


class IPSourceBBIPField(str, Enum):
    LINK = "link"
    INTERFACE = "interface"
    STATUS = "status"
    LAYER = "layer"


class IPSourceBBIPEntity(BaseModel):
    id: PyObjectId | None = None
    link: str
    interface: str
    layer: str
    status: str = SourceStatus.ACTIVE.value

    @field_validator("layer")
    @classmethod
    def layer_must_be_valid_ip(cls, v):
        if not ValidatorConfig.valid_layer_ip(v):
            raise ValueError(
                f"La capa '{v}' no está definida en la configuración del sistema"
            )
        return v
