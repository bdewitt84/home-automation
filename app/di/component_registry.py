from typing import (
    Callable,
    Any,
    Type,
    Optional
)

from app.di.registry import ComponentMetadata


class DuplicateKeyError(Exception):
    pass


class FactoryNotFoundError(Exception):
    pass


class TypeNotFoundError(Exception):
    pass


class ComponentRegistry:
    def __init__(self):
        self._factories: dict[str, Callable] = {}
        self._singletons: dict[str, Any] = {}
        self._metadata: dict[str, ComponentMetadata] = {}
        self._type_to_key: dict[Type, str] = {}

    def add_component(self,
                      key: str,
                      factory: Callable,
                      metadata: ComponentMetadata,
                      is_dependency: bool = False) -> None:
        """
        Stores the factory and metadata.
        If is_dependency is True, it also maps the class type to this key.
        """
        if key in self._factories:
            raise DuplicateKeyError(f"Key '{key}' is already registered")

        if is_dependency and metadata.type in self._type_to_key:
            raise DuplicateKeyError(f"Type '{metadata.type.__name__}' is already mapped to a key")

        self._factories[key] = factory
        self._metadata[key] = metadata
        if is_dependency:
            self._type_to_key[metadata.type] = key

    def store_singleton(self, key: str, instance: Any) -> None:
        """Caches a resolved instance."""
        self._singletons[key] = instance

    def get_factory(self, key: str) -> Optional[Callable]:
        """Retrieves the factory recipe for a key."""
        try:
            return self._factories[key]
        except KeyError:
            raise FactoryNotFoundError(f"No factory registered for key '{key}'")

    def get_singleton(self, key: str) -> Optional[Any]:
        """Retrieves a cached instance if it exists."""
        return self._singletons.get(key, None)

    def get_metadata(self, key: str) -> Optional[ComponentMetadata]:
        """Retrieves the metadata 'ID card' for a key."""
        return self._metadata.get(key, None)

    def get_key_by_type(self, cls: Type) -> Optional[str]:
        """The 'Type-to-Key' bridge. Finds the key associated with a class type."""
        try:
            return self._type_to_key[cls]
        except KeyError:
            raise TypeNotFoundError(f"Type '{cls.__name__}' is not registered as a dependency")

    def get_all_metadata(self) -> dict[str, ComponentMetadata]:
        """Returns the full metadata dictionary for scanning/discovery."""
        return self._metadata.copy()

    def is_registered(self, key: str) -> bool:
        """Checks if a key exists in the registry."""
        return key in self._factories

    def is_dependency(self, cls: Type[Any]) -> bool:
        return cls in self._type_to_key

    def get_registered_keys(self):
        return list(self._factories.keys())

    def get_lifecycle_keys(self):

        keys = [
            key for key, metadata
            in self._metadata.items()
            if metadata.lifecycle > 0
        ]
        return sorted(keys, key=lambda k: self.get_metadata(k).lifecycle)
