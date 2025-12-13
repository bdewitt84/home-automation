# app/wiring.py

"""
    Handles getting singletons from factories and attaching them to the
    application's dependency container
"""

from fastapi import FastAPI
from app.di.container import DependencyContainer
from app.di.factories.vlc_process_manager_factory import VlcProcessManagerFactory

from app.di.keys import (
    MEDIA_CONTROL_KEY,
    EVENT_BUS_KEY,
    APP_SETTINGS_KEY,
    CONTAINER_KEY,
    MEDIA_CONTROL_SERVICE_KEY, VLC_PROCESS_MANAGER_KEY,
)

from app.di.factories import (
    VlcMediaControlFactory,
    ASyncEventBusFactory,
    MediaControlServiceFactory,
)

from config.settings import settings
from events.event_bus import ASyncEventBus


def get_dependency_container(app: FastAPI) -> DependencyContainer:
    """
    Get dependency container from applicaiton state. Container is initialized
    in app.main.py
    :param app: FastAPI application
    :returns: dependency container
    """
    container: DependencyContainer = getattr(app.state, CONTAINER_KEY)
    return container


def register_media_controller(container: DependencyContainer):
    """
    Registers the media controller component with the dependency container.
    :param container: dependency container
    :returns: None
    """
    container.register_singleton(
        MEDIA_CONTROL_KEY,
        lambda: VlcMediaControlFactory(container).create(),
    )


def register_event_bus(container: DependencyContainer):
    """
    Registers the asyncronous event bus with the dependency container
    and starts the event bus.
    :param container: dependency container
    :returns: None
    """
    container.register_singleton(
        EVENT_BUS_KEY,
        lambda: ASyncEventBusFactory(container).create(),
    )


def start_event_bus(container: DependencyContainer):
    bus: ASyncEventBus = container.resolve(EVENT_BUS_KEY)
    bus.start()


def register_settings(container: DependencyContainer) -> None:
    """
    Registers an instance of Pydantic BaseSettings containing application
    configuration settings. The settings are already initialized and are
    imported from config.settings.settings
    :param container: dependency container
    :returns: None
    """
    container.register_singleton(
        APP_SETTINGS_KEY,
        lambda: settings,
    )


def register_media_service(container: DependencyContainer) -> None:
    """
    Registers the media service singleton with the dependency container
    :param container: dependency container
    :returns: None
    """
    container.register_singleton(
        MEDIA_CONTROL_SERVICE_KEY,
        lambda: MediaControlServiceFactory(container).create(),
    )


def register_vlc_process_manager(container: DependencyContainer) -> None:
    """
    Registers the vlc process manager singleton with the dependency container
    :param container: dependency container
    :returns: None
    """
    container.register_singleton(
        VLC_PROCESS_MANAGER_KEY,
        lambda: VlcProcessManagerFactory(container).create(),
    )


async def start_vlc_process_manager(container: DependencyContainer) -> None:
    vlc_process_manager = container.resolve(VLC_PROCESS_MANAGER_KEY)
    await vlc_process_manager.start()
