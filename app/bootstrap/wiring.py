# app/bootstrap/wiring.py

from typing import Type, Any

from app.di.container import DependencyContainer
from app.di.registry import ComponentMetadata
from app.lifecycle_manager import LifeCycleManager


def wire_infrastructure_components(registry: dict[Type[Any], ComponentMetadata],
                                   container: DependencyContainer,
                                   ) -> None:

    for _component_cls, metadata in registry.items():
        if metadata.is_dependency:
            try:
                container.register_component(metadata.key, _component_cls, metadata, overrides=None)

            except Exception as e:
                raise RuntimeError(f"Critical wiring failure for {_component_cls.__name__}: {e}") from e


def get_metadata_by_key(key: str,
    registry: dict[Type[Any], ComponentMetadata],
    )-> ComponentMetadata | None:

    for metadata in registry.values():
        if metadata.key == key:
            return metadata

    return None


def wire_user_components(config_data: dict,
                         container: DependencyContainer,
                         registry: dict[Type[Any], ComponentMetadata],
                         ) -> None:

    components_config = config_data.get('components', {})

    for component_name, component_data in components_config.items():

        type_name = component_data['type']
        metadata = get_metadata_by_key(type_name, registry)
        if not metadata:
            print(f"Warning: No metadata found for component type '{type_name}'")
            continue

        settings_cls = metadata.settings_cls
        settings_data = component_data.get('settings', {})
        settings_instance = settings_cls(**settings_data)
        overrides = {'settings': settings_instance}

        container.register_component(
            key=component_name,
            cls=metadata.type,
            metadata=metadata,
            overrides=overrides,
        )


def wire_lifecycle_management(container: DependencyContainer,
                              manager: LifeCycleManager
                              ) -> None:
    for key in container.get_lifecycle_keys():
        instance = container.resolve(key)
        manager.index_singleton(instance)
