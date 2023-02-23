# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

from fastapi import APIRouter
from fastapi import FastAPI
from fastramqpi.main import FastRAMQPI  # type: ignore
from ramqp.mo import MORouter  # type: ignore
from ramqp.mo.models import ObjectType  # type: ignore
from ramqp.mo.models import PayloadType

from .config import get_settings
from .log import setup_logging
from elevate_manager.mo import get_client

amqp_router = MORouter()
fastapi_router = APIRouter()


@fastapi_router.post("/dummy/test")
async def dummy() -> dict[str, str]:
    return {"foo": "bar"}


@amqp_router.register("*.*.*")
async def listener(context: dict, payload: PayloadType, **kwargs: Any) -> None:
    print("HURRA")
    print(payload)
    print(kwargs)

    routing_key = kwargs["mo_routing_key"]

    if routing_key.object_type == ObjectType.MANAGER:
        print("Manager UUID", payload.object_uuid)


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

    return fastramqpi


def create_app(**kwargs) -> FastAPI:
    fastramqpi = create_fastramqpi(**kwargs)
    return fastramqpi.get_app()
