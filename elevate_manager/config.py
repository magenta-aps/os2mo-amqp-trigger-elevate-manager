# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import cast

from fastramqpi.config import Settings as FastRAMQPISettings  # type: ignore
from pydantic import AmqpDsn
from pydantic import AnyHttpUrl
from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class Settings(BaseSettings):
    """Settings for the engagement elevator AMQP trigger."""

    log_level: str = "INFO"

    class Config:
        """Settings are frozen."""

        frozen = True
        env_nested_delimiter = "__"

    amqp_url: AmqpDsn = Field(cast(AmqpDsn, "amqp://guest:guest@msg_broker"))

    auth_realm: str = Field(
        "mo", description="Base URL for OS2mo. Will authenticate against this Realm."
    )

    auth_server: AnyHttpUrl = Field(
        cast(AnyHttpUrl, "http://keycloak-service:8080/auth"),
        description="Base URL for OIDC server, which is Keycloak.",
    )

    client_id: str = Field(
        "integration_engagement_elevator", description="Client ID for Keycloak."
    )

    client_secret: str | None = Field(..., description="Client secret for Keycloak.")

    fastramqpi: FastRAMQPISettings = Field(
        default_factory=FastRAMQPISettings, description="FastRAMQPI settings."
    )

    mo_url: AnyHttpUrl = Field(
        cast(AnyHttpUrl, "http://mo-service:5000"),
        description="Base URL for OS2mo.",
    )


def get_settings(*args, **kwargs) -> Settings:
    return Settings(*args, **kwargs)
