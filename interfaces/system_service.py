# /interfaces/system_service.py

from abc import ABC, abstractmethod
from app.models.system import SystemResult


class SystemService(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def reboot(self) -> SystemResult:
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> SystemResult:
        raise NotImplementedError
