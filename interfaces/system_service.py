# /interfaces/system_service.py

from abc import ABC, abstractmethod


class SystemService(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def reboot(self):
        raise NotImplementedError

    @abstractmethod
    def shutdown(self):
        raise NotImplementedError
