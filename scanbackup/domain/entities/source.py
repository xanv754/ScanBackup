from bson import ObjectId
from pydantic import BaseModel
from scanbackup.shared import SourceStatus
from scanbackup.shared import LayerBBIP


class BBIPSourceEntity(BaseModel):
    """Data structure of the daily report."""

    id: ObjectId
    link: str
    interface: str
    capacity: float
    type: str
    status: SourceStatus
    layer: LayerBBIP


class IPDailySummaryEntity(BaseModel):
    """Data structure of the daily report."""

    id: ObjectId
    link: str
    interface: float
    status: SourceStatus
    layer: LayerBBIP
