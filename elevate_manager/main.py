# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

import structlog
from fastapi import APIRouter
from fastapi import FastAPI
from fastramqpi.main import FastRAMQPI  # type: ignore
from ramqp.mo import MORouter  # type: ignore
from ramqp.mo.models import PayloadType  # type: ignore

from .config import get_settings
from .events import process_manager_event
from .log import setup_logging
from .mo import get_client

amqp_router = MORouter()
fastapi_router = APIRouter()

logger = structlog.get_logger(__name__)


@fastapi_router.post("/dummy/test")
async def dummy() -> dict[str, str]:
    return {"foo": "bar"}


@amqp_router.register("org_unit.manager.*")
async def listener(context: dict, payload: PayloadType, **kwargs: Any) -> None:
    gql_client = context["user_context"]["gql_client"]
    print("*****************", payload.object_uuid)
    await process_manager_event(gql_client, payload.object_uuid)


def create_fastramqpi(**kwargs) -> FastRAMQPI:
    settings = get_settings()
    setup_logging(settings.log_level)

    fastramqpi = FastRAMQPI(
        application_name="os2mo-manager-elevator", settings=settings.fastramqpi
    )

    amqpsystem = fastramqpi.get_amqpsystem()
    amqpsystem.router.registry.update(amqp_router.registry)

    app = fastramqpi.get_app()
    app.include_router(fastapi_router)

    gql_client = get_client(
        mo_url=settings.fastramqpi.mo_url,
        client_id=settings.fastramqpi.client_id,
        client_secret=settings.fastramqpi.client_secret.get_secret_value(),
        auth_realm=settings.fastramqpi.auth_realm,
        auth_server=settings.fastramqpi.auth_server,
    )
    fastramqpi.add_context(gql_client=gql_client)

    return fastramqpi


def create_app(**kwargs) -> FastAPI:
    fastramqpi = create_fastramqpi(**kwargs)
    return fastramqpi.get_app()
