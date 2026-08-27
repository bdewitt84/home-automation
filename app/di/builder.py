# ./app/di/builder.py

from app.di.container import DependencyContainer
from app.di.registry import (
    ComponentMetadata,
    MetadataRegistry,
)
from app.exceptions.di import (
    DependencyNotFoundError,
    CycleDetectedError,
    IllegalDependencyError, GraphValidationError,
)
from app.models.config import Config


class ContainerBuilder:
    def __init__(self,
                 container: DependencyContainer,
                 registry: MetadataRegistry,
                 config: Config):
        self._container = container
        self._registry: MetadataRegistry = registry
        self._config = config
        self._component_graph: dict[str, dict] = {}

    def build(self) -> None:
        self._container.register_self()
        self._wire_infrastructure()
        self._wire_user_components()
        self._build_dependency_graph()
        self._validate_dependency_graph()

    def _wire_core(self, instances: list[Any]) -> None:
        self._logger.info(msg="\tWiring core...")
        for instance in instances:
            self._container.register_instance(key=instance.__class__.__name__,
                                              instance=instance)

    def _wire_infrastructure(self) -> None:
        for _component_cls, metadata in self._registry.items():
            if metadata.is_dependency:
                try:
                    self._container.register_component(
                        key=metadata.key,
                        cls=_component_cls,
                        metadata=metadata,
                        overrides=None
                    )

                except Exception as e:
                    raise RuntimeError(
                        f"Critical wiring failure for infrastructure component '{_component_cls.__name__}': {e}") from e

    def _wire_user_components(self) -> None:

        for component_name, component_data in self._config.components.items():

            metadata = self._get_metadata_by_key(component_data.type)
            settings = component_data.settings
            overrides = {}

            if settings:
                overrides = {'settings': component_data.settings}

            try:
                self._container.register_component(
                    key=component_name,
                    cls=metadata.type,
                    metadata=metadata,
                    overrides=overrides,
                )

            except Exception as e:
                raise RuntimeError(f"Critical wiring failure for component '{component_name}': {e}") from e

    def _get_metadata_by_key(self, key: str)-> ComponentMetadata | None:
        for metadata in self._registry.values():
            if metadata.key == key:
                return metadata

    def _build_dependency_graph(self) -> None:
        for key, record in self._container.get_all_records().items():
            dependencies: dict[str, str] = {}

            for name, requirement in record.metadata.requirements.items():
                if name in record.overrides:
                    continue

                req_key = self._container.get_key_by_type(requirement.type)

                if req_key is None:
                    if requirement.has_default:
                        continue
                    raise DependencyNotFoundError(f"Dependency '{name}' not found for component '{key}'")

                dependencies[name] = req_key

            self._component_graph[key] = {
                "requires": dependencies,
                "is_dependency": record.metadata.is_dependency,
            }

    def _validate_graph_dfs_rec(self, cur: str, path: list, safe: set) -> None:
        if cur in safe:
            return
        if cur in path:
            raise CycleDetectedError(f"Cycle detected validating {cur}: {' -> '.join(path + [cur])}")

        try:
            node = self._component_graph[cur]
        except KeyError as e:
            raise GraphValidationError(f"Dependency '{cur}' not found") from e

        if not node["is_dependency"] and len(path) > 0:
            parent = path[-1]
            raise IllegalDependencyError(f"Component '{cur}' cannot depend on '{parent}' because it is not a dependency")

        path.append(cur)
        for req_key in node["requires"].values():
            self._validate_graph_dfs_rec(req_key, path, safe)
        safe.add(cur)
        path.pop()

    def _validate_dependency_graph(self) -> None:
        path: list[str] = []
        safe: set = {self.__class__.__name__}
        for key in self._component_graph.keys():
            self._validate_graph_dfs_rec(key, path, safe)
