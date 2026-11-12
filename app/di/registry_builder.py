# ./app/di/registry_builder.py


from typing import Any, Optional, Callable, Type

from app.di.component_registry import ComponentRegistry
from app.di.container import DependencyContainer
from app.di.registry import MetadataRegistry
from app.models.component import ComponentMetadata, DependencyRequirement
from app.models.config import Config
from components.infrastructure.system_logger import SystemLogger


class RegistryBuilder:

    def __init__(self,
                 logger: SystemLogger,
                 metadata: MetadataRegistry,
                 config: Config,
                 core: list[Any] = None):
        self._logger = logger
        self._metadata = metadata
        self._config = config
        self._core = core
        self._registry: ComponentRegistry = ComponentRegistry()

    def build(self):
        self._register_core(self._core)
        self._register_infrastructure()
        self._register_user_components()
        return self._registry

    def _register_core(self, _core):
        self._logger.info(msg="\tWiring core...")
        for instance in self._core:
            try:
                self._register_instance(
                    key=instance.__class__.__name__,
                    instance=instance
                )
            except Exception as e:
                self._logger.error(f"Critical wiring failure for core component '{instance}': {e}")
                raise

    def _register_infrastructure(self):
        self._logger.info(msg="\tWiring infrastructure...")
        for _component_cls, metadata in self._metadata.items():
            if metadata.is_dependency:
                try:
                    self._register_component(
                        key=metadata.key,
                        cls=_component_cls,
                        metadata=metadata,
                        overrides=None
                    )

                except Exception as e:
                    self._logger.error(
                        f"Critical wiring failure for infrastructure component '{_component_cls.__name__}': {e}"
                    )
                    raise

    def _register_user_components(self):
        self._logger.info(msg="\tWiring user components...")
        for component_name, component_data in self._config.components.items():

            metadata = self._get_metadata_by_key(component_data.type)
            settings = component_data.settings
            overrides = {}

            if settings:
                overrides = {'settings': component_data.settings}

            try:
                self._register_component(
                    key=component_name,
                    cls=metadata.type,
                    metadata=metadata,
                    overrides=overrides,
                )

            except Exception as e:
                # TODO: Log this
                raise RuntimeError(f"Critical wiring failure for component '{component_name}': {e}") from e

    def _get_metadata_by_key(self, key: str) -> ComponentMetadata | None:
        for metadata in self._metadata.values():
            if metadata.key == key:
                return metadata

    @staticmethod
    def _create_factory(cls,
                        requirements: dict[str, DependencyRequirement],
                        overrides: Optional[dict[str, Any]] = None
                        ) -> Callable[[], Any]:

        overrides = overrides or {}

        def factory(container: DependencyContainer):
            needed_from_container = {}
            for name, requirement in requirements.items():
                if overrides and name in overrides:
                    continue
                if container._get_key_by_type(requirement.type) is None and requirement.has_default:
                    continue
                needed_from_container[name] = requirement

            resolved_dependencies = container._get_resolved_dependencies(needed_from_container)
            return cls(**resolved_dependencies, **overrides)

        return factory

    def _register_component(self,
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
        self._register_factory(key, factory, overrides, metadata)

    def _register_factory(self,
                          key: str,
                          factory: Callable[[], Any],
                          overrides: dict[str, Any],
                          metadata: ComponentMetadata = None,
                          ) -> None:

        self._registry.add_component(key=key,
                                     factory=factory,
                                     overrides=overrides,
                                     metadata=metadata)

    def _get_key_by_type(self, cls: Type) -> Optional[str]:
        return self._registry.get_key_by_type(cls)

    def _register_instance(self, key: str, instance: Any) -> None:
        self._register_factory(
            key=key,
            factory=lambda: instance,
            overrides={},
            metadata=ComponentMetadata(
                key=key,
                type=instance.__class__,
                is_dependency=True
            )
        )
