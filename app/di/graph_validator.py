# ./app/di/graph_validator.py


from app.exceptions.di import CycleDetectedError, GraphValidationError, IllegalDependencyError
from app.di.graph_builder import ComponentGraph
from components.infrastructure.system_logger import SystemLogger


class GraphValidator:
    def __init__(self,
                 logger: SystemLogger,
                 graph: ComponentGraph,
                 ):
        self._logger = logger
        self._component_graph = graph

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
            # TODO: Decide how to log and propagate errors
            m = f"Component '{cur}' cannot depend on '{parent}' because it is not a dependency"
            self._logger.error(m)
            raise IllegalDependencyError(m)

        path.append(cur)
        for req_key in node["requires"].values():
            self._validate_graph_dfs_rec(req_key, path, safe)
        safe.add(cur)
        path.pop()

    def validate_graph(self) -> None:
        self._logger.info("\tValidating dependency graph...")
        path: list[str] = []
        safe: set = set()
        for key in self._component_graph.keys():
            self._validate_graph_dfs_rec(key, path, safe)
