# app.state.py

from fastapi import FastAPI

from app.wiring import get_dependency_container, register_settings, register_and_start_event_bus, \
    register_media_controller, register_media_service
from events.event_bus import ASyncEventBus
from app.dependencies.container_keys import (
    CONTAINER_KEY,
    EVENT_BUS_KEY,
)


def configure_state(app: FastAPI) -> None:

    container = get_dependency_container(app)


    # --- Register Application Singletons ---

    register_settings(container)
    register_and_start_event_bus(container)


    # --- Register Component Singletons ---

    register_media_controller(container)


    # --- Register Service Singletons ---

    register_media_service(container)


def shutdown_state(app: FastAPI) -> None:
    container = getattr(app.state, CONTAINER_KEY)
    bus:ASyncEventBus = container.resolve(EVENT_BUS_KEY)
    bus.stop()
