# app/dependencies/providers.py

from app.container import DependencyContainer
from interfaces.media_control_interface import MediaControlInterface
from events.event_bus import ASyncEventBus
from fastapi import Request, HTTPException
from config.app_config import MEDIA_CONTROL_KEY, CONTAINER_KEY, EVENT_BUS_KEY, MEDIA_CONTROL_SERVICE_KEY
from services.media.media_control_service import MediaControlService


def get_media_control_service(request: Request) -> MediaControlService:
    try:
        container: DependencyContainer = getattr(request.app.state, CONTAINER_KEY)
        media_control_service = container.resolve(MEDIA_CONTROL_SERVICE_KEY)
        return media_control_service
    except KeyError:
        raise HTTPException(
            status_code=500,
            detail="Application misconfiguration: media control service not registered."
        )


def get_media_controller(request: Request) -> MediaControlInterface:

    try:
        container: DependencyContainer = getattr(request.app.state, CONTAINER_KEY)
        media_controller = container.resolve(MEDIA_CONTROL_KEY)
        return media_controller

    except KeyError:
        raise HTTPException(
            status_code=500,
            detail="Application misconfiguration: media controller not registered.",
        )

def get_event_bus(request: Request) -> ASyncEventBus:
    try:
        container: DependencyContainer = getattr(request.app.state, CONTAINER_KEY)
        bus = container.resolve(EVENT_BUS_KEY)
        return bus
    except KeyError:
        raise HTTPException(
            status_code=500,
            detail="Application misconfiguration: event bus not registered.",
        )

def get_dependency(request: Request, key: str) -> any:
    try:
        container: DependencyContainer = getattr(request.app.state, CONTAINER_KEY)
        dependency = container.resolve(key)
        return dependency
    except KeyError:
        raise HTTPException(
            status_code=500,
            detail=f"Application misconfiguration: {key} not registered.",
        )
