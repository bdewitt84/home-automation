# app/di/factories/async_event_bus_factory.py

from interfaces.factory_interface import FactoryInterface
from app.di.keys import MEDIA_CONTROL_KEY, EVENT_BUS_KEY
from app.di.container import DependencyContainer
from components.services.media.media_control_service import MediaControlService


class MediaControlServiceFactory(FactoryInterface):

    def __init__(self, container: DependencyContainer):
        super().__init__(container)

    def create(self):

        # Acquire dependencies
        media_controller = self._container.resolve(MEDIA_CONTROL_KEY)
        event_bus = self._container.resolve(EVENT_BUS_KEY)

        # Create instance
        media_control_service = MediaControlService(
            media_controller,
            event_bus
        )

        return media_control_service
