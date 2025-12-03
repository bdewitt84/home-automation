# app/dependencies/providers.py
from app.container import DependencyContainer
from interfaces.media_control_interface import MediaControlInterface
from fastapi import Request, HTTPException
from config.app_config import MEDIA_CONTROL_KEY, CONTAINER_KEY


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
