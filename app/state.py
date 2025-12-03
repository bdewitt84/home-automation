# app.state.py

from fastapi import FastAPI
from app.container import DependencyContainer

from app.dependencies.factories import vlc_media_control_factory
from config.app_config import MEDIA_CONTROL_URL, MEDIA_CONTROL_PASSWORD, MEDIA_CONTROL_KEY
from config.app_config import CONTAINER_KEY


def configure_state(app: FastAPI) -> None:
    container: DependencyContainer = getattr(app.state, CONTAINER_KEY)
    container.register_singleton(
        MEDIA_CONTROL_KEY,
        lambda: vlc_media_control_factory(
            MEDIA_CONTROL_URL,
            MEDIA_CONTROL_PASSWORD
        )
    )

