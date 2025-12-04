# api/v1/media_router.py

from fastapi import APIRouter, Depends
from services.media import media_control_service
from app.dependencies.providers import get_media_control_service
from services.media.media_control_service import MediaControlService


media_router = APIRouter(
    tags=["media"],
)


@media_router.get("/play")
async def media_play(media_control_service: MediaControlService = Depends(get_media_control_service)) -> dict:
    return media_control_service.play()


@media_router.get("/stop")
async def media_stop() -> dict:
    return media_control_service.stop()


@media_router.get("/enqueue")
async def media_enqueue(path: str) -> dict:
    return media_control_service.enqueue(path)
