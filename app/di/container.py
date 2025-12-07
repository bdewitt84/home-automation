# app/di/container.py

from typing import Callable, Any

class DependencyContainer:
    def __init__(self):
        self._singletons: dict[str, Any] = {}
        self._factories: dict[str, Callable[[], Any]] = {}

    def register_singleton(self, key: str, factory: Callable[[], Any]) -> None:
        if key in self._factories:
            raise ValueError(f"Dependency '{key}' already registered")

        self._factories[key] = factory

    def resolve(self, key: str) -> Any:
        if key not in self._singletons:
            if key not in self._factories:
                raise ValueError(f"Dependency '{key}' not registered")

            factory = self._factories[key]
            singleton = factory()
            self._singletons[key] = singleton

        return self._singletons[key]
