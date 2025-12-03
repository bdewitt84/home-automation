# api/v1/system_router.py

from fastapi import APIRouter, Depends

from interfaces.media_control_interface import MediaControlInterface
from services.media import media_control_service
from app.dependencies.providers import get_media_controller


media_router = APIRouter(
    tags=["media"],
)


@media_router.get("/play")
async def media_play(media_controller: MediaControlInterface = Depends(get_media_controller)) -> dict:
    return media_control_service.play(media_controller)


@media_router.get("/stop")
async def media_stop() -> dict:
    return media_control_service.stop()


@media_router.get("/enqueue")
async def media_enqueue(path: str) -> dict:
    return media_control_service.enqueue(path)
