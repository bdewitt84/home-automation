# ./app/di/builder.py

from app.di.container import DependencyContainer
from app.di.registry import ComponentMetadata, ComponentRegistry


class ContainerBuilder:
    def __init__(self, registry: ComponentRegistry, config: dict):
        self._registry: ComponentRegistry = registry
        self._config = config
        self._container: DependencyContainer | None = None

    def build(self) -> DependencyContainer:
        self._container = DependencyContainer()
        self._container.register_self()
        self._wire_infrastructure()
        self._wire_user_components()
        self._verify_dependency_graph()
        return self._container

    def _wire_infrastructure(self) -> None:
        for _component_cls, metadata in self._registry.items():
            if metadata.is_dependency:
                try:
                    self._container.register_component(metadata.key, _component_cls, metadata, overrides=None)

                except Exception as e:
                    raise RuntimeError(
                        f"Critical wiring failure for infrastructure component '{_component_cls.__name__}': {e}") from e


    def _wire_user_components(self) -> None:
        # TODO: Change config to DTO
        components_config = self._config.get('components', {})

        for component_name, component_data in components_config.items():

            type_name = component_data['type']
            metadata = self._get_metadata_by_key(type_name)

            # TODO: Move validation to config loader
            if not metadata:
                print(f"Warning: No metadata found for component type '{type_name}'")
                continue

            settings_cls = metadata.settings_cls
            settings_data = component_data.get('settings', {})
            settings_instance = settings_cls(**settings_data)
            overrides = {'settings': settings_instance}

            # TODO: Add to try block
            self._container.register_component(
                key=component_name,
                cls=metadata.type,
                metadata=metadata,
                overrides=overrides,
            )

    def _get_metadata_by_key(self, key: str)-> ComponentMetadata | None:
        for metadata in self._registry.values():
            if metadata.key == key:
                return metadata

    def _verify_dependency_graph(self):
        self._container.validate_graph_dfs()
