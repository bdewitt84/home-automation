# app/di/factories/async_event_bus_factory.py

from events.event_bus import ASyncEventBus
from interfaces.factory_interface import FactoryInterface
from app.di.container import DependencyContainer


class ASyncEventBusFactory(FactoryInterface):
    def __init__(self, container: DependencyContainer):
        super().__init__(container)

    def create(self):
        return ASyncEventBus()
