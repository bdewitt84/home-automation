# app/di/lifecycle_manager.py

from typing import Any
from interfaces import LifecycleManagementInterface


class LifeCycleManager:
    def __init__(self):
        self._singletons: [LifecycleManagementInterface] = []

    def index_singleton(self, singleton: Any):
        if isinstance(singleton, LifecycleManagementInterface):
            print(f"Indexed {singleton.__class__.__name__} with lifecycle manager")
            self._singletons.append(singleton)

    async def start_registered(self):
        print(f"Starting lifecycle for {[singleton.__class__.__name__ for singleton in self._singletons]}")
        for singleton in self._singletons:
            print(f"Calling start on {singleton.__class__.__name__}")
            await singleton.start()

    async def stop_registered(self):
        for singleton in reversed(self._singletons):
            print(f"Calling stop on {singleton.__class__.__name__}")
            await singleton.stop()
