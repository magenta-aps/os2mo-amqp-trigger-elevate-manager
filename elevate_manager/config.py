# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastramqpi.config import Settings as FastRAMQPISettings  # type: ignore
from pydantic.env_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the engagement elevator AMQP trigger."""

    log_level: str = "INFO"

    class Config:
        """Settings are frozen."""

        frozen = True
        env_nested_delimiter = "__"

    fastramqpi: FastRAMQPISettings
