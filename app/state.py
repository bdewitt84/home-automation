# app.state.py

from fastapi import FastAPI
from app.container import DependencyContainer
from config.settings import settings
from events.event_bus import ASyncEventBus
from app.dependencies.container_keys import (
    MEDIA_CONTROL_KEY,
    CONTAINER_KEY,
    EVENT_BUS_KEY,
    MEDIA_CONTROL_SERVICE_KEY,
    SYSTEM_SERVICE_KEY,
    APP_SETTINGS_KEY,
)
from app.dependencies.factories import (
    vlc_media_control_factory,
    async_event_bus_factory,
    # system_service_factory,
    media_control_service_factory,
)


def configure_state(app: FastAPI) -> None:

    # Get dependency container
    container: DependencyContainer = getattr(app.state, CONTAINER_KEY)

    # Register settings
    container.register_singleton(
        APP_SETTINGS_KEY,
        lambda: settings,
    )

    # Register media controller
    container.register_singleton(
        MEDIA_CONTROL_KEY,
        lambda: vlc_media_control_factory(container),
    )

    # Register event bus
    container.register_singleton(
        EVENT_BUS_KEY,
        lambda: async_event_bus_factory()
    )
    bus: ASyncEventBus = container.resolve(EVENT_BUS_KEY)
    bus.start()

    # --- Register Services ---

    # Register Media Service
    container.register_singleton(
        MEDIA_CONTROL_SERVICE_KEY,
        lambda: media_control_service_factory(container)
    )

    # # Register System Service
    # container.register_singleton(
    #     SYSTEM_SERVICE_KEY,
    #     lambda: system_service_factory()
    # )


def shutdown_state(app: FastAPI) -> None:
    container = getattr(app.state, CONTAINER_KEY)
    bus:ASyncEventBus = container.resolve(EVENT_BUS_KEY)
    bus.stop()
