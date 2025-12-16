# components/media_control_service.py

from interfaces.media_control_interface import MediaControlInterface
from events.event_bus import ASyncEventBus
# from events.media import MediaPlayEvent


class MediaControlService:
    def __init__(self, media_control: MediaControlInterface, bus: ASyncEventBus):
        self.media_control = media_control
        self.bus = bus


    def play(self) -> dict:
        status = self.media_control.play()
        # extract status information for event
        # self.bus.publish(MediaPlayEvent())
        return status.model_dump()


    def stop(self) -> dict:
        return {'message': 'stop stub'}


    def enqueue(self, file_path: str) -> dict:
        return {'message': 'enqueue stub'}
