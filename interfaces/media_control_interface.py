# interfaces/media_control_interface.py

from abc import ABC, abstractmethod
from interfaces.schemas import MediaControlStatus


class MediaControlInterface(ABC):

    @abstractmethod
    def play(self) -> MediaControlStatus:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> MediaControlStatus:
        raise NotImplementedError

    @abstractmethod
    def enqueue(self, filepath: str) -> MediaControlStatus:
        raise NotImplementedError