# app/dependencies/providers.py

from interfaces.media_control_interface import MediaControlInterface
from fastapi import Request
from config.app_config import MEDIA_CONTROL_KEY


def get_media_controller(request: Request) -> MediaControlInterface:
    media_controller = getattr(request.app.state, MEDIA_CONTROL_KEY, None)
    return media_controller
