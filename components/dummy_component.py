from app.di.registry import register_component_with_container
from components.infrastructure import AsyncHttpClient
from interfaces import LifecycleManagementInterface


@register_component_with_container(register_at_startup=False, lifecycle=1000)
class DummyComponent(LifecycleManagementInterface):
    def __init__(self, http_client: AsyncHttpClient, settings: dict):
        self.http_client = http_client
        if self.http_client is None:
            raise RuntimeError('http_client must be provided')

    async def start(self):
        pass

    async def stop(self):
        pass
