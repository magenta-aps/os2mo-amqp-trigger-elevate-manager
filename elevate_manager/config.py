# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastramqpi.config import Settings as FastRAMQPISettings  # type: ignore
from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class Settings(BaseSettings):
    fastramqpi: FastRAMQPISettings = Field(
        default_factory=FastRAMQPISettings, description="FastRAMQPI settings"
    )

    class Config:
        frozen = True
        env_nested_delimiter = "__"


def get_settings(*args, **kwargs) -> Settings:
    return Settings(*args, **kwargs)
