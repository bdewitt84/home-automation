# interfaces/factory_interface

from abc import ABC, abstractmethod
from app.di.container import DependencyContainer


class FactoryInterface(ABC):
    def __init__(self, container: DependencyContainer):
        self._container = container

    @abstractmethod
    def create(self):
        raise NotImplementedError
