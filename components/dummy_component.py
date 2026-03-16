from pydantic import BaseModel

from app.di.registry import component
from components.infrastructure import AsyncHttpClient
from interfaces import LifecycleManagement


class DummyComponentSettings(BaseModel):
    mock_setting_a: int
    mock_setting_b: int


@component(is_dependency=False,
           lifecycle=1000,
           settings_cls=DummyComponentSettings)

class DummyComponent(LifecycleManagement):
    def __init__(self, http_client: AsyncHttpClient, settings: DummyComponentSettings):
        self.http_client = http_client
        self.settings = settings
        if self.http_client is None:
            raise RuntimeError('http_client must be provided')

    async def start(self):
        print(f"Starting with settings: {self.settings.mock_setting_a}")

    async def stop(self):
        print(f"Stopping with settings: {self.settings.mock_setting_b}")
