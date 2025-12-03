# app/dependencies/providers.py

from interfaces.media_control_interface import MediaControlInterface
from fastapi import Request


def get_media_controller(request: Request) -> MediaControlInterface:
    media_controller = getattr(request.app.state, 'media_control_instance', None)
    return media_controller
