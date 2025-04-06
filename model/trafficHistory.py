from pydantic import BaseModel


class TrafficHistoryModel(BaseModel):
    """Traffic model of layers history."""

    date: str
    time: str
    id_layer: str
    type_layer: str
    in_prom: int
    in_max: int
    out_prom: int
    out_max: int
