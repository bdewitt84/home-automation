# app/di/container.py

from typing import Callable, Any, Type, Optional
from inspect import signature

from app.di.component_registry import ComponentRegistry
from app.di.registry import ComponentMetadata


class DependencyContainer:
    def __init__(self, registry: Optional[ComponentRegistry]=None):
        self._registry = registry or ComponentRegistry()

    def register_factory(self,
                         key: str,
                         factory: Callable[[], Any],
                         metadata: ComponentMetadata = None,
                         is_dependency: bool = False,
                         ) -> None:

        self._registry.add_component(key, factory, metadata, is_dependency)

    def resolve(self, key: str) -> Any:
        instance = self._registry.get_singleton(key)
        if instance is None:
            factory = self._registry.get_factory(key)
            instance = factory()
            self._registry.store_singleton(key, instance)
        return instance

    def resolve_by_type(self, target:Type[Any]) -> Any:
        key = self._registry.get_key_by_type(target)
        return self.resolve(key)

    def get_metadata(self, key:str) -> Any:
        return self._registry.get_metadata(key)

    def get_all_registered_metadata(self):
        return self._registry.get_all_metadata()

    def get_registered_component_keys(self) -> list[str]:
        return self._registry.get_registered_keys()

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

            if not self._registry.is_dependency(arg_type) and name not in overrides:
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
        self.register_factory(key, factory, metadata, is_dependency)

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
        self._registry.map_type_to_key(cls, key)

    def register_self(self):

        name = self.__class__.__name__
        type_ = self.__class__
        factory = lambda: self

        metadata = ComponentMetadata(name, type_)
        self.register_factory(name, factory, metadata, is_dependency=True)
