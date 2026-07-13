from typing import (
    Callable,
    Any,
    Type,
    Optional
)

from app.exceptions.di import DuplicateKeyError, MetadataNotFoundError
from app.models.component import ComponentMetadata, ComponentRegistration


class ComponentRegistry:
    def __init__(self):
        self._singletons: dict[str, Any] = {}
        self._type_to_key: dict[Type, str] = {}
        self._component_records: dict[str, ComponentRegistration] = {}

    def add_component(self,
                      key: str,
                      factory: Callable,
                      overrides: dict[str, Any],
                      metadata: ComponentMetadata,
                      ) -> None:
        """
        Stores the factory and metadata.
        If is_dependency is True, it also maps the class type to this key.
        """

        if key in self._component_records:
            raise DuplicateKeyError(f"Key '{key}' is already registered")

        if metadata is None:
            raise MetadataNotFoundError(f"Metadata not found for component with key '{key}'")

        if metadata.is_dependency and metadata.type in self._type_to_key:
            raise DuplicateKeyError(f"Type '{metadata.type.__name__}' is already mapped to a key")

        new_record = ComponentRegistration(
            factory=factory,
            metadata=metadata,
            overrides=overrides,
        )
        self._component_records[key] = new_record

        if metadata.is_dependency:
            self._type_to_key[metadata.type] = key

    def store_singleton(self, key: str, instance: Any) -> None:
        """Caches a resolved instance."""
        self._singletons[key] = instance

    def get_singleton(self, key: str) -> Optional[Any]:
        """Retrieves a cached instance if it exists."""
        return self._singletons.get(key, None)

    def get_factory(self, key: str) -> Optional[Callable]:
        """Retrieves the factory recipe for a key."""
        record = self._component_records.get(key, None)
        return record.factory if record else None

    def get_metadata(self, key: str) -> Optional[ComponentMetadata]:
        """Retrieves the metadata 'ID card' for a key."""
        record = self._component_records.get(key, None)
        return record.metadata if record else None

    def get_key_by_type(self, cls: Type) -> Optional[str]:
        """The 'Type-to-Key' bridge. Finds the key associated with a class type."""
        return self._type_to_key.get(cls, None)

    def get_all_metadata(self) -> dict[str, ComponentMetadata]:
        """Returns the full metadata dictionary for scanning/discovery."""
        return {
            key:record.metadata
            for key, record
            in self._component_records.items()
        }

    def is_registered(self, key: str) -> bool:
        """Checks if a key exists in the registry."""
        return key in self._component_records

    def is_dependency(self, cls: Type[Any]) -> bool:
        return cls in self._type_to_key

    def get_registered_keys(self):
        return list(self._component_records.keys())

    def get_lifecycle_keys(self):

        keys = [
            key
            for key, record
            in self._component_records.items()
            if record.metadata.lifecycle > 0
        ]
        return sorted(keys, key=lambda k: self.get_metadata(k).lifecycle)

    def get_record(self, key: str) -> ComponentRegistration:
        return self._component_records.get(key, None)
