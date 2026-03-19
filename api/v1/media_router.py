# api/v1/media_router.py

from fastapi import APIRouter, Depends, HTTPException

from app.di.container import DependencyContainer
from components.services.media import media_control_service
from api.providers import get_media_control_service, get_container
from components.services.media.media_control_service import MediaControlService


media_router = APIRouter(
    tags=["media"],
)


# @media_router.get("/{component_name}/play")
async def media_play(component_name:str,
                     media_service: MediaControlService = Depends(get_media_control_service),
                     ) -> dict:
    try:
        return await media_service.play(component_name)

    except TypeError as e:
        raise HTTPException(status_code=500, detail=str(e))


# @media_router.get("/")
async def media_root():
    return {"media root hit": {}}
