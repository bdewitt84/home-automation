# app/di/lifecycle_manager.py

from typing import Any
from interfaces import LifecycleManagementInterface


class LifeCycleManager:
    def __init__(self):
        self._singletons: [LifecycleManagementInterface] = []

    def index_singleton(self, singleton: Any):
        # Don't index non-lifecycle instances
        if not isinstance(singleton, LifecycleManagementInterface):
            return

        # Don't index an instance twice. This is a policy violation, so we raise
        if singleton in self._singletons:
            raise ValueError("Singleton already indexed")

        self._singletons.append(singleton)
        print(f"Indexed {singleton.__class__.__name__} with lifecycle manager")

    async def start_registered(self):
        print(f"Starting lifecycle for {[singleton.__class__.__name__ for singleton in self._singletons]}")

        for singleton in self._singletons:
            print(f"Calling start on {singleton.__class__.__name__}")
            try:
                await singleton.start()

            # Crash if a component fails to start. No half-alive systems.
            # lifespan will call shutdown, don't attempt to roll-back here.
            except Exception as e:
                print(f"Failed to start {singleton.__class__.__name__}.")
                raise e

    async def stop_registered(self):
        for singleton in reversed(self._singletons):
            try:
                print(f"Stopping {singleton.__class__.__name__}")
                await singleton.stop()

            # Log and let the exception fall through. Stop as many components as possible.
            except Exception as e:
                print(f"Could not stop {singleton.__class__.__name__}: {e}.")
