import os

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from interface_sync.constants.constants import (
    DEFAULT_MONGO_AUTH_SOURCE,
    MONGO_AUTH_SOURCE_VARIABLE,
    MONGO_DATABASE_VARIABLE,
    MONGO_HOST_VARIABLE,
    MONGO_PASSWORD_VARIABLE,
    MONGO_PORT_VARIABLE,
    MONGO_USERNAME_VARIABLE,
)
from interface_sync.exceptions import MissingDatabaseSettingsError


class MongoSettings(BaseModel):
    """Connection settings of MongoDB. The password is hidden from `repr`."""

    model_config = ConfigDict(frozen=True)

    host: str = Field(min_length=1)
    port: int = Field(gt=0, le=65535)
    username: str = Field(min_length=1)
    password: str = Field(min_length=1, repr=False)
    database: str = Field(min_length=1)
    auth_source: str = Field(min_length=1)

    @classmethod
    def from_environment(cls) -> "MongoSettings":
        """Read the settings; raise `MissingDatabaseSettingsError` if one is missing or invalid."""
        values = {
            variable: os.environ.get(variable, "")
            for variable in (
                MONGO_HOST_VARIABLE,
                MONGO_PORT_VARIABLE,
                MONGO_USERNAME_VARIABLE,
                MONGO_PASSWORD_VARIABLE,
                MONGO_DATABASE_VARIABLE,
            )
        }
        missing = [variable for variable, value in values.items() if not value]
        if missing:
            raise MissingDatabaseSettingsError(
                f"Configuración de la base de datos ausente: {', '.join(missing)}"
            )
        try:
            return cls(
                host=values[MONGO_HOST_VARIABLE],
                port=values[MONGO_PORT_VARIABLE],  # type: ignore
                username=values[MONGO_USERNAME_VARIABLE],
                password=values[MONGO_PASSWORD_VARIABLE],
                database=values[MONGO_DATABASE_VARIABLE],
                auth_source=os.environ.get(MONGO_AUTH_SOURCE_VARIABLE) or DEFAULT_MONGO_AUTH_SOURCE,
            )
        except ValidationError as error:
            raise MissingDatabaseSettingsError(
                f"{MONGO_PORT_VARIABLE} debe ser un número de puerto válido"
            ) from error
