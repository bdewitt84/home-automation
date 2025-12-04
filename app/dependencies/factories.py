# app.dependencies.factories

from app.container import DependencyContainer
from config.app_config import MEDIA_CONTROL_KEY, EVENT_BUS_KEY
from services.media.vlc_media_control import VLCMediaControl
from services.media.media_control_service import MediaControlService
# from services.system_service import SystemService
from events.event_bus import ASyncEventBus


def vlc_media_control_factory(url: str, password: str):
    return VLCMediaControl(url, password)


def async_event_bus_factory():
    return ASyncEventBus()


# def system_service_factory():
#     return SystemService()


def media_control_service_factory(container: DependencyContainer):

    # Acquire dependencies
    media_controller = container.resolve(MEDIA_CONTROL_KEY)
    event_bus = container.resolve(EVENT_BUS_KEY)

    # Create instance
    media_control_service = MediaControlService(
        media_controller,
        event_bus
    )

    return media_control_service