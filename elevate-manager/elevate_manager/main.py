from fastapi import APIRouter
from fastapi import FastAPI

from fastramqpi.main import FastRAMQPI
from ramqp.mo import MORouter
from ramqp.mo.models import PayloadType

from .config import get_settings

amqp_router = MORouter()
fastapi_router = APIRouter()


@fastapi_router.post("/dummy/test")
async def dummy() -> dict[str, str]:
    return {"foo": "bar"}


@amqp_router.register("*.*.*")
async def listener(context: dict, payload: PayloadType) -> None:
    print(payload)


def create_fastramqpi(**kwargs) -> FastRAMQPI:
    settings = get_settings()

    fastramqpi = FastRAMQPI(
        application_name="os2mo-manager-elevator",
        settings=settings.fastramqpi
    )

    amqpsystem = fastramqpi.get_amqpsystem()
    amqpsystem.router.registry.update(amqp_router.registry)

    app = fastramqpi.get_app()
    app.include_router(fastapi_router)

    return fastramqpi


def create_app(**kwargs) -> FastAPI:
    fastramqpi = create_fastramqpi(**kwargs)
    return fastramqpi.get_app()
