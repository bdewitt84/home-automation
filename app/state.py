# app.state.py

from fastapi import FastAPI
from services.media.vlc_media_control import VLCMediaControl
from config.app_config import MEDIA_CONTROL_KEY, MEDIA_CONTROL_URL, MEDIA_CONTROL_PASSWORD


def create_media_controller_singleton(app: FastAPI):
    vlc_media_control_instance = VLCMediaControl(
        MEDIA_CONTROL_URL,
        MEDIA_CONTROL_PASSWORD,
    )
    setattr(
        app.state,
        MEDIA_CONTROL_KEY,
        vlc_media_control_instance
    )


def configure_state(app: FastAPI):
    create_media_controller_singleton(app)

