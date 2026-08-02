# ./app/bootstrap/parser.py

from app.exceptions.di import MetadataNotFoundError
from app.models.component import ComponentMetadata
from app.models.config import Config, ConfigComponent
from app.di.registry import MetadataRegistry


class ConfigParser:
    def __init__(self, registry: MetadataRegistry=None):
        self._registry = registry

    def _get_metadata_by_key(self, type_name: str) -> ComponentMetadata | None:
        for metadata in self._registry.values():
            if metadata.key == type_name:
                return metadata
        return None

    def parse_config(self, config: dict) -> Config:

        components = {
            name: self._parse_component(name, data)
            for name, data in config.get("components", {}).items()
        }

        validated_config = Config(
            version=config.get("version", "unknown"),
            app_settings=config.get("app_settings", {}),
            components=components,
        )

        return validated_config

    def _parse_component(self, name: str, component_data: dict):
        type_name = component_data.get("type")
        raw_settings = component_data.get("settings", {})

        metadata = self._get_metadata_by_key(type_name)
        if metadata is None:
            raise MetadataNotFoundError(
                f"Component type '{type_name}' not found in the registry"
            )

        settings_instance = None
        if metadata.settings_cls:
            settings_model = metadata.settings_cls
            try:
                settings_instance = settings_model(**raw_settings)
            except Exception as e:
                raise ValueError(
                    f"Invalid settings '{settings_model.__name__}' for component '{type_name}': {e}") from e

        return ConfigComponent(
            name=name,
            type=type_name,
            settings=settings_instance,
        )
