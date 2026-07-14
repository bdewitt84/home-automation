# app/di/container.py

from typing import Callable, Any, Type, Optional

from fastapi.exceptions import ValidationException

from app.di.component_registry import ComponentRegistry
from app.exceptions.di import CycleDetectedError, DependencyNotFoundError, FactoryNotFoundError, TypeNotFoundError
from app.models.component import ComponentMetadata, ComponentRegistration


class GraphValidationError(Exception): pass

class MetadataNotFoundError(GraphValidationError): pass


class DependencyContainer:
    def __init__(self,
                 registry: Optional[ComponentRegistry]=None,):

        self._registry = registry or ComponentRegistry()


    def register_factory(self,
                         key: str,
                         factory: Callable[[], Any],
                         overrides: dict[str, Any],
                         metadata: ComponentMetadata = None,
                         ) -> None:

        self._registry.add_component(key=key,
                                     factory=factory,
                                     overrides=overrides,
                                     metadata=metadata)

    def resolve(self, key: str) -> Any:
        instance = self._registry.get_singleton(key)

        if instance is None:
            factory = self._registry.get_factory(key)

            if factory is None:
                raise FactoryNotFoundError(f"Cannot resolve key '{key}': Factory is not registered")

            instance = factory()
            self._registry.store_singleton(key, instance)

        return instance

    def resolve_by_type(self, target:Type[Any]) -> Any:
        key = self._registry.get_key_by_type(target)

        if key is None:
            raise TypeNotFoundError(f"Cannot resolve for type '{target.__name__}': Type is not registered")

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
                           metadata: ComponentMetadata,
                           overrides: Optional[dict[str, Any]] = None
                           ) -> None:
        if not isinstance(metadata, ComponentMetadata):
            raise ValueError(f"Cannot register component '{key}': "
                             f"Component metadata must be an instance of 'ComponentMetadata'.")

        overrides = overrides or {}
        requirements = metadata.requirements
        factory = self._create_factory(cls, requirements, overrides)
        self.register_factory(key, factory, overrides, metadata)

    def register_self(self):

        name = self.__class__.__name__
        type_ = self.__class__
        factory = lambda: self

        metadata = ComponentMetadata(name, type_, is_dependency=True)
        self.register_factory(key=name,
                              factory=factory,
                              overrides={},
                              metadata=metadata,)

    def validate_graph(self):
        for key, metadata in self._registry.get_all_metadata().items():

            if metadata.type == self.__class__:
                continue

            requirements = metadata.requirements
            overrides = {}

            try:
                self._validate(requirements, overrides)

            except Exception as e:
                raise ValidationException(f"Error validating {metadata.type} with key {key}: {e}") from e


    def _validate_graph_dfs_rec(self, cur: str, path: list, safe: set):
        if cur in safe:
            return
        if cur in path:
            raise CycleDetectedError(f"Cycle detected validating {cur}: {' -> '.join(path + [cur])}")

        metadata = self._registry.get_metadata(cur)

        if not self._registry.is_dependency(metadata.type) and len(path) > 0:
            parent = path[-1]
            raise GraphValidationError(f"Component '{cur}' cannot depend on '{parent}' because it is not a dependency")

        path.append(cur)
        cur_overrides = self._registry.get_record(cur).overrides
        for req_name, req_type in metadata.requirements.items():
            if req_name in cur_overrides:
                continue
            req_key = self._registry.get_key_by_type(req_type)
            if not req_key:
                raise DependencyNotFoundError(f"Component {cur} requires Dependency '{req_type.__name__}', "
                                              f"but it has no registered key")
            self._validate_graph_dfs_rec(req_key, path, safe)

        safe.add(cur)
        path.pop()


    def validate_graph_dfs(self):
        path: list[str] = []
        safe: set = {self.__class__.__name__}
        for key in self._registry.get_all_metadata().keys():
            self._validate_graph_dfs_rec(key, path, safe)

    def get_record(self, key: str) -> ComponentRegistration:
        return self._registry.get_record(key)
