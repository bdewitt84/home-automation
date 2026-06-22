# app/di/container.py

from typing import Callable, Any, Type, Optional

from fastapi.exceptions import ValidationException

from app.di.component_registry import ComponentRegistry
from app.di.introspector import Introspector
from app.di.registry import ComponentMetadata


class DependencyNotFoundError(Exception): pass


class DependencyContainer:
    def __init__(self,
                 registry: Optional[ComponentRegistry]=None,
                 inspector: Optional[Introspector]=None):
        self._registry = registry or ComponentRegistry()
        self._inspector = inspector or Introspector()

    def register_factory(self,
                         key: str,
                         factory: Callable[[], Any],
                         metadata: ComponentMetadata = None,
                         ) -> None:

        self._registry.add_component(key, factory, metadata)

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

    def get_lifecycle_keys(self):
        return self._registry.get_lifecycle_keys()

    def _get_resolved_dependencies(self, requirements: dict[str, Type]) -> dict[str, Any]:

        resolved = {
            name: self.resolve_by_type(arg_type)
            for name, arg_type in requirements.items()
        }

        return resolved

    def _validate(self,
                      requirements: dict[str, Type],
                      overrides: Optional[dict[str, Any]]):

        for cls_name, arg_type in requirements.items():

            if cls_name in overrides:
                continue

            if not self._registry.is_dependency(arg_type):
                raise DependencyNotFoundError(
                    f"Validation error: '{cls_name}': ({arg_type.__name__}) "
                    f"is not a registered dependency and no override was provided."
                )

    def _create_factory(self,
                        cls,
                        requirements: dict[str, Type],
                        overrides: Optional[dict[str, Any]] = None) -> Callable[[], Any]:
        def factory():
            needed_from_container = {
                name: type_
                for name, type_ in requirements.items()
                if name not in overrides
            }
            resolved_dependencies = self._get_resolved_dependencies(needed_from_container)
            return cls(**resolved_dependencies, **overrides)

        return factory

    def register_component(self,
                           key: str,
                           cls: Type[Any],
                           metadata: ComponentMetadata = None,
                           overrides: Optional[dict[str, Any]] = None
                           ) -> None:

        overrides = overrides or {}

        requirements = self._inspector.get_requirements(cls)
        # self._validate(requirements, overrides)
        factory = self._create_factory(cls, requirements, overrides)
        self.register_factory(key, factory, metadata)

    def register_self(self):

        name = self.__class__.__name__
        type_ = self.__class__
        factory = lambda: self

        metadata = ComponentMetadata(name, type_, is_dependency=True)
        self.register_factory(name, factory, metadata)

    def validate_graph(self):
        for key, metadata in self._registry.get_all_metadata().items():

            if metadata.type == self.__class__:
                continue

            cls = metadata.type
            requirements = self._inspector.get_requirements(cls)
            overrides = {}

            try:
                self._validate(requirements, overrides)

            except Exception() as e:
                raise ValidationException(f"Error validating {metadata.type} with key {key}: {e}") from e
