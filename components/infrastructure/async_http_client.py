# ./components/async_http_client.py

import httpx
from typing import Optional, Type

from app.di.keys import ASYNC_HTTP_CLIENT_KEY
from app.di.registry import register_component_with_container
from interfaces import LifecycleManagementInterface


@register_component_with_container(ASYNC_HTTP_CLIENT_KEY, 100)
class AsyncHttpClient(LifecycleManagementInterface):
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None

    async def start(self):
        # self.client = httpx.AsyncClient()
        pass

    async def stop(self):
        # await self.client.aclose()
        pass

    async def get(self, request_url: str, params: Optional[dict] = None, auth=Type[tuple[str, str]]) -> httpx.Response:
        response = await self.client.get(request_url, params=params, auth=auth)
        return response
