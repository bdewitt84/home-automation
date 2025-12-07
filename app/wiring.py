# app/wiring.py

"""
    Handles getting singletons from factories and attaching them to the
    application's dependency container
"""

from fastapi import FastAPI
from app.container import DependencyContainer

from app.dependencies.container_keys import (
    MEDIA_CONTROL_KEY,
    EVENT_BUS_KEY,
    APP_SETTINGS_KEY,
    CONTAINER_KEY,
    MEDIA_CONTROL_SERVICE_KEY,
)

from app.dependencies.factories import (
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
    :param app:
    :return:
    """
    container: DependencyContainer = getattr(app.state, CONTAINER_KEY)
    return container


def register_media_controller(container: DependencyContainer):
    """
    Registers the media controller component with the dependency container.
    :param container: dependency container
    :return: None
    """
    container.register_singleton(
        MEDIA_CONTROL_KEY,
        lambda: VlcMediaControlFactory(container).create(),
    )


def register_and_start_event_bus(container: DependencyContainer):
    """
    Registers the asyncronous event bus with the dependency container
    and starts the event bus.
    :param container:
    :return:
    """
    container.register_singleton(
        EVENT_BUS_KEY,
        lambda: ASyncEventBusFactory(container).create(),
    )
    bus: ASyncEventBus = container.resolve(EVENT_BUS_KEY)
    bus.start()


def register_settings(container: DependencyContainer) -> None:
    """
    Registers an instance of Pydantic BaseSettings containing application
    configuration settings. The settings are already initialized and are
    imported from config.settings.settings
    :param container:
    :return:
    """
    container.register_singleton(
        APP_SETTINGS_KEY,
        lambda: settings,
    )


def register_media_service(container):
    """
    Registers the media service singleton with the dependency container
    :param container:
    :return:
    """
    container.register_singleton(
        MEDIA_CONTROL_SERVICE_KEY,
        lambda: MediaControlServiceFactory(container).create(),
    )
