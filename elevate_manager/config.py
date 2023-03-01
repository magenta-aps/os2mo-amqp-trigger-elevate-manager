# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import cast

from fastramqpi.config import Settings as FastRAMQPISettings  # type: ignore
from pydantic import AmqpDsn
from pydantic import Field
from pydantic.env_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the engagement elevator AMQP trigger."""

    log_level: str = "INFO"

    class Config:
        """Settings are frozen."""

        frozen = True
        env_nested_delimiter = "__"

    amqp_url: AmqpDsn = Field(cast(AmqpDsn, "amqp://guest:guest@msg_broker"))

    fastramqpi: FastRAMQPISettings = Field(
        default_factory=FastRAMQPISettings, description="FastRAMQPI settings."
    )


def get_settings(*args, **kwargs) -> Settings:
    return Settings(*args, **kwargs)
