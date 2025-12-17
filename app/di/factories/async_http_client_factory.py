# app/di/factories/async_http_client_factory.py

from interfaces import FactoryInterface
from app.di.container import DependencyContainer
from components.infrastructure import AsyncHttpClient


class AsyncHttpClientFactory(FactoryInterface):
    def __init__(self, container: DependencyContainer):
        super().__init__(container)

    def create(self) -> AsyncHttpClient:
        return AsyncHttpClient()
