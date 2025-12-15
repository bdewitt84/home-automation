# app/di/lifecycle_manager.py

from typing import Any
from interfaces import LifecycleManagementInterface


class LifeCycleManager:
    def __init__(self):
        self._singletons = []

    def index_singleton(self, singleton: Any):
        if isinstance(singleton, LifecycleManagementInterface):
            self._singletons.append(singleton)

    async def start_registered(self):
        for singleton in self._singletons:
            await singleton.start()

    async def stop_registered(self):
        for singleton in reversed(self._singletons):
            await singleton.stop()
