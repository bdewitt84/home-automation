# ./app/di/graph_builder.py


from typing import TypeAlias

from app.di.component_registry import ComponentRegistry
from app.exceptions.di import DependencyNotFoundError
from components.infrastructure.system_logger import SystemLogger


ComponentGraph: TypeAlias = dict[str, dict]


class GraphBuilder:
    def __init__(self,
                 logger: SystemLogger,
                 registry: ComponentRegistry,):

        self._component_graph: ComponentGraph = {}
        self._registry = registry
        self._logger = logger

    def build_dependency_graph(self) -> ComponentGraph:
        self._logger.info(msg="\tBuilding dependency graph...")
        for key, record in self._registry.get_all_records().items():
            dependencies: dict[str, str] = {}

            for name, requirement in record.metadata.requirements.items():
                if name in record.overrides:
                    continue

                req_key = self._registry.get_key_by_type(requirement.type)

                if req_key is None:
                    if requirement.has_default:
                        continue
                    # TODO: log this
                    raise DependencyNotFoundError(f"Dependency '{name}' not found for component '{key}'")

                dependencies[name] = req_key

            self._component_graph[key] = {
                "requires": dependencies,
                "is_dependency": record.metadata.is_dependency,
            }

        return self._component_graph
