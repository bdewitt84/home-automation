# app/di/container.py

from typing import Any, Type, Optional

from app.di.component_registry import ComponentRegistry
from app.exceptions.di import (
    FactoryNotFoundError,
    TypeNotFoundError,
)
from app.models.component import (
    DependencyRequirement,
)


class DependencyContainer:
    def __init__(self,
                 registry: Optional[ComponentRegistry] = None,):

        self._registry = registry or ComponentRegistry()

    def resolve(self, key: str) -> Any:
        instance = self._registry.get_singleton(key)

        if instance is None:
            factory = self._registry.get_factory(key)

            if factory is None:
                raise FactoryNotFoundError(f"Cannot resolve key '{key}': Factory is not registered")

            instance = factory(self)
            self._registry.store_singleton(key, instance)

        return instance

    def resolve_by_type(self, target: Type[Any]) -> Any:
        key = self._registry.get_key_by_type(target)

        if key is None:
            raise TypeNotFoundError(f"Cannot resolve for type '{target.__name__}': Type is not registered")

        return self.resolve(key)

    def get_metadata(self, key: str) -> Any:
        return self._registry.get_metadata(key)

    def get_all_registered_metadata(self):
        return self._registry.get_all_metadata()

    def get_lifecycle_keys(self):
        return self._registry.get_lifecycle_keys()

    def _get_resolved_dependencies(self, requirements: dict[str, DependencyRequirement]) -> dict[str, Any]:
        return {
            name: self.resolve_by_type(requirement.type)
            for name, requirement
            in requirements.items()
        }

    def _get_key_by_type(self, cls: Type) -> Optional[str]:
        return self._registry.get_key_by_type(cls)
