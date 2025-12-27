# app/di/container.py

from typing import Callable, Any
from inspect import signature


class DependencyContainer:
    def __init__(self):
        self._singletons: dict[str, Any] = {}
        self._factories: dict[str, Callable[[], Any]] = {}
        self._class_to_key = {}

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

    def get_registered_singleton_keys(self) -> list[Any]:
        return list(self._factories.keys())

    def _create_instance_by_auto_injection(self, cls: type) -> Any:

        kwargs = {}
        params = signature(cls).parameters.items()

        for keyword, param in params:

            arg_type = param.annotation

            if arg_type is None:
                raise ValueError(f"Parameter {keyword} has no annotation")

            if arg_type not in self._class_to_key.keys():
                raise ValueError(f"Class '{keyword}' not registered with container")

            key = self._class_to_key.get(arg_type)
            instance = self.resolve(key)
            kwargs.update({keyword: instance})


    def register_singleton_by_inspection(self, key: str, cls: type) -> None:

        self._class_to_key.update({cls: key})

        def auto_factory():
            return self._create_instance_by_auto_injection(cls)

        self.register_singleton(key, auto_factory)


    def map_class_to_key(self, cls: type, key: str) -> None:
        self._class_to_key[cls] = key
