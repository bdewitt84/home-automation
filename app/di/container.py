# app/di/container.py

from typing import Callable, Any, Type, Optional
from inspect import signature

from app.di.registry import ComponentMetadata


class DependencyContainer:
    def __init__(self):
        self._singletons: dict[str, Any] = {}
        self._factories: dict[str, Callable[[], Any]] = {}
        self._type_registry: dict[Type[Any], str] = {}
        self._metadata_registry: dict[str, ComponentMetadata] = {}

    def register_factory(self,
                         key: str,
                         factory: Callable[[], Any],
                         metadata: ComponentMetadata = None
                         ) -> None:

        if key in self._factories:
            raise ValueError(f"Dependency '{key}' already registered")

        self._factories[key] = factory
        self._metadata_registry[key] = metadata

    def resolve(self, key: str) -> Any:
        if key not in self._singletons:
            if key not in self._factories:
                raise ValueError(f"Dependency '{key}' not registered")

            factory = self._factories[key]
            singleton = factory()
            self._singletons[key] = singleton

        return self._singletons[key]

    def resolve_by_type(self, target:Type[Any]) -> Any:

        if target not in self._type_registry:
            raise ValueError(f"Dependency '{target}' not registered")

        key = self._type_registry[target]
        return self.resolve(key)

    def get_metadata(self, key: str) -> Any:
        if key not in self._metadata_registry:
            raise ValueError(f"Metadata for '{key}' not registered")
        return self._metadata_registry[key]

    def get_all_registered_metadata(self) -> dict[str, ComponentMetadata]:
        return self._metadata_registry

    def get_registered_component_keys(self) -> list[Any]:
        return list(self._factories.keys())

    def _get_constructor_requirements(self,
                                      cls: Type[Any],
                                      overrides: Optional[dict[str, Any]] = None,
                                      ) -> dict[str, Type]:
        sig = signature(cls)
        requirements = {}
        if not overrides: overrides = {}

        for name, param in sig.parameters.items():
            arg_type = param.annotation

            if arg_type is param.empty:
                raise ValueError(f"Parameter {name} has no annotation")

            if arg_type is None:
                raise ValueError(f"Parameter {name} must not have annotation 'None'")

            if arg_type not in self._type_registry and name not in overrides:
                raise ValueError(f"Could not create instance of {cls.__name__}: Parameter '{name}' of type '{arg_type}' not registered with container and not found in overrides")

            requirements[name] = arg_type

        return requirements

    def _get_resolved_dependencies(self, requirements: dict[str, Type]) -> dict[str, Any]:

        resolved = {
            name: self.resolve_by_type(arg_type)
            for name, arg_type in requirements.items()
        }

        return resolved

    def _register_component(self,
                            key: str,
                            cls: Type[Any],
                            metadata: ComponentMetadata = None,
                            is_dependency: bool = False,
                            overrides: Optional[dict[str, Any]] = None
                            ) -> None:

        if is_dependency:
            self._type_registry.update({cls: key})

        overrides = overrides or {}

        requirements = self._get_constructor_requirements(cls, overrides)
        
        def factory():
            needed_from_container = {
                name: type_
                for name, type_ in requirements.items()
                if name not in overrides
            }
            dependencies = self._get_resolved_dependencies(needed_from_container)
            return cls(**dependencies, **overrides)
        
        print(f"Container: Registering {cls.__name__} with key {key}, overrides {overrides.keys()}")
        self.register_factory(key, factory, metadata)

    def register_as_dependency(self,
                               key: str,
                               cls: Type[Any],
                               metadata: ComponentMetadata = None
                               ) -> None:

        self._register_component(key, cls, metadata, is_dependency=True)

    def register_named_component(self,
                                 key: str,
                                 cls: Type[Any],
                                 metadata: ComponentMetadata,
                                 overrides: Optional[dict[str, Any]] = None
                                 ) -> None:

        self._register_component(key, cls, metadata, is_dependency=False, overrides=overrides)

    def map_type_to_key(self, cls: Type[Any], key: str) -> None:
        self._type_registry[cls] = key

    def register_self(self):

        name = self.__class__.__name__
        type_ = self.__class__
        factory = lambda: self

        metadata = ComponentMetadata(name, type_)
        self.register_factory(name, factory, metadata)

        self.map_type_to_key(type_, name)
