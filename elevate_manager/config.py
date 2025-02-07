# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastramqpi.config import Settings as FastRAMQPISettings  # type: ignore
from pydantic import BaseModel
from pydantic import BaseSettings


class ElevateManagerSettings(BaseModel):
    """Settings for the manager terminator AMQP trigger."""

    log_level: str = "INFO"


class Settings(BaseSettings):
    """Settings for the engagement elevator AMQP trigger."""

    log_level: str = "INFO"

    class Config:
        """Settings are frozen."""

        frozen = True
        env_nested_delimiter = "__"

    fastramqpi: FastRAMQPISettings
    elevate_manager: ElevateManagerSettings = ElevateManagerSettings()
