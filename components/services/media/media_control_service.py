# components/media_control_service.py

from app.di.container import DependencyContainer
from app.di.registry import component
from interfaces.media_control_interface import MediaControlInterface
from components.infrastructure.event_bus import ASyncEventBus
from interfaces.schemas import MediaControlStatus
# from events.media import MediaPlayEvent


@component(is_dependency=True)
class MediaControlService:
    def __init__(self, container: DependencyContainer, bus: ASyncEventBus):
        self.container = container
        self.bus = bus


    async def play(self, component_name: str) -> dict:

        controller: MediaControlInterface = self.container.resolve(component_name)

        if not isinstance(controller, MediaControlInterface):
            raise TypeError(f"{component_name} {(type(controller.__name__))} is not a MediaControlInterface")

        status: MediaControlStatus = await controller.play()

        return status.model_dump()

    def stop(self) -> dict:
        return {'message': 'stop stub'}

    def enqueue(self, file_path: str) -> dict:
        return {'message': 'enqueue stub'}
