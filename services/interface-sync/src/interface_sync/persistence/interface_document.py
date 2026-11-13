from datetime import datetime

from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId

from interface_sync.constants.enums import InterfaceStatus


class InterfaceDocument(BaseModel):
    """A document of the `interfaces` collection; mirrors `.claude/docs/database.md`.

    `id` is the internal `_id` and is `None` until the document is stored. Dates are
    timezone-aware UTC `datetime`. `capacity_gbps` is always a `float`.
    """

    id: PydanticObjectId | None = None
    layer: str
    name: str
    vendor: str
    capacity_gbps: float
    scan_url: str
    status: InterfaceStatus
    created_at: datetime
    updated_at: datetime
