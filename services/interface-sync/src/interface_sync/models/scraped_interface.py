from pydantic import BaseModel, ConfigDict


class ScrapedInterface(BaseModel):
    """An interface as shown by a SCAN listing page, before any validation.

    `position` is the 1-based place of the interface in the listing. A `None` value
    means the datum could not be obtained; later validations decide what that implies.
    Layer and vendor are not part of it: they come from the page configuration.
    """

    model_config = ConfigDict(frozen=True)

    position: int
    name: str | None
    scan_url: str | None
    capacity_gbps: float | None
