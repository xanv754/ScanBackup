from pydantic import BaseModel, field_validator
from scanbackup.domain.services.validator import ValidatorConfig
from scanbackup.shared import SourceStatus


class BBIPTrafficSourceEntity(BaseModel):
    link: str
    interface: str
    capacity: float
    type: str
    status: str = SourceStatus.ACTIVE.value
    layer: str

    @field_validator("layer")
    @classmethod
    def layer_must_be_valid_bbip(cls, v):
        if not ValidatorConfig.valid_layer_bbip(v):
            raise ValueError(
                f"La capa '{v}' no está definida en la configuración del sistema"
            )
        return v
