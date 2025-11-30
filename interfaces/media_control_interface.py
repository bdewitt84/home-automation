# interfaces/media_control_interface.py

from abc import ABC, abstractmethod
from pydantic import BaseModel


class MediaControlStatus(BaseModel):
    state: str = "N/A"
    volume: int = 0
    time: int = 0
    length: int = 0


class MediaControlInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def play(self) -> MediaControlStatus:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> MediaControlStatus:
        raise NotImplementedError

    @abstractmethod
    def enqueue(self, filepath: str) -> MediaControlStatus:
        raise NotImplementedError