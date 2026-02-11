from app.di.container import DependencyContainer
from app.di.registry import component


@component(is_dependency=True)
class DiscoveryService:
    def __init__(self, container: DependencyContainer):
        self._container = container

    def get_services_by_type(self, target_type):
        results = {}

        for key, metadata in self._container.get_all_registered_metadata().items():
            if issubclass(metadata.type, target_type):
                results[key] = self._container.resolve(key)

    def list_all_named_components(self):
        return {
            key:metadata
            for key, metadata
            in self._container.get_all_registered_metadata().items()
            if metadata.is_dependency is False
        }
