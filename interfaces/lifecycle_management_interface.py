# interfaces/lifecycle_management_interface.py

from abc import ABC, abstractmethod


class LifecycleManagement(ABC):

    @abstractmethod
    async def start(self):
        raise NotImplementedError

    @abstractmethod
    async def stop(self):
        raise NotImplementedError
