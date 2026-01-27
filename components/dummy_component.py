from pydantic import BaseModel

from app.di.registry import register_component_with_container
from components.infrastructure import AsyncHttpClient
from interfaces import LifecycleManagementInterface


class DummyComponentSettings(BaseModel):
    mock_setting_a: int
    mock_setting_b: int


@register_component_with_container(register_at_startup=False,
                                   lifecycle=1000,
                                   settings_cls=DummyComponentSettings)

class DummyComponent(LifecycleManagementInterface):
    def __init__(self, http_client: AsyncHttpClient, settings: DummyComponentSettings):
        self.http_client = http_client
        self.settings = settings
        if self.http_client is None:
            raise RuntimeError('http_client must be provided')

    async def start(self):
        print(f"Starting with settings: {self.settings.mock_setting_a}")

    async def stop(self):
        print(f"Stopping with settings: {self.settings.mock_setting_b}")
