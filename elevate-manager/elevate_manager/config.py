from pydantic.env_settings import BaseSettings

from fastramqpi.config import Settings as FastRAMQPISettings
from pydantic.fields import Field


class Settings(BaseSettings):
    fastramqpi: FastRAMQPISettings = Field(
        default_factory=FastRAMQPISettings,
        description="FastRAMQPI settings"
    )

    class Config:
        frozen = True
        env_nested_delimiter = "__"


def get_settings(*args, **kwargs) -> Settings:
    return Settings(*args, **kwargs)
