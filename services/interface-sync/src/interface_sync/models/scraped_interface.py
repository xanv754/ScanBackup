from pydantic import BaseModel, ConfigDict


class ScrapedInterface(BaseModel):
    """An interface as shown by a SCAN listing page, before any validation.

    `position` is the 1-based place of the interface in the listing. A `None` value
    means the datum could not be obtained; later validations decide what that implies.
    The layer always comes from the page configuration. The vendor does too, unless the
    parser sets its own (`vendor`), as the Bras layer does to tell Uplink from Downlink.
    """

    model_config = ConfigDict(frozen=True)

    position: int
    name: str | None
    scan_url: str | None
    capacity_gbps: float | None
    vendor: str | None = None
