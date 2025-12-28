# app/di/container.py

from typing import Callable, Any, Type
from inspect import signature


class DependencyContainer:
    def __init__(self):
        self._singletons: dict[str, Any] = {}
        self._factories: dict[str, Callable[[], Any]] = {}
        self._type_registry = {}

    def register_factory(self, key: str, factory: Callable[[], Any]) -> None:
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

    def get_registered_component_keys(self) -> list[Any]:
        return list(self._factories.keys())

    def _get_constructor_requirements(self, cls: type) -> dict[str, Type]:
        sig = signature(cls)
        requirements = {}

        for name, param in sig.parameters.items():
            arg_type = param.annotation

            if arg_type is param.empty:
                raise ValueError(f"Parameter {name} has no annotation")

            if arg_type is None:
                raise ValueError(f"Parameter {name} must not have annotation 'None'")

            if arg_type not in self._type_registry:
                raise ValueError(f"Could not create instance of {cls.__name__}: Parameter '{name}' of type '{arg_type}' not registered with container")

            requirements[name] = arg_type

        return requirements

    def _get_resolved_dependencies(self, requirements: dict[str, Type]) -> dict[str, Any]:

        resolved = {
            name: self.resolve(self._type_registry[arg_type])
            for name, arg_type in requirements.items()
        }

        return resolved

    def register_class(self, key: str, cls: type) -> None:
        self._type_registry.update({cls: key})

        requirements = self._get_constructor_requirements(cls)

        def auto_factory():
            dependencies = self._get_resolved_dependencies(requirements)
            return cls(**dependencies)

        print(f"Container: Registering {cls.__name__} with key {key}")
        self.register_factory(key, auto_factory)

    def map_type_to_key(self, cls: type, key: str) -> None:
        self._type_registry[cls] = key
