# app/bootstrap/scanner.py

import importlib
from typing import Type, Any, Callable, Iterator, IO
from types import ModuleType
import os
import re
from json import load

from app.di.container import DependencyContainer
from app.di.registry import ComponentMetadata, METADATA_INDEX
from app.lifecycle_manager import LifeCycleManager
from interfaces import FactoryInterface

from config.project import FACTORY_PACKAGE_PATH

ModuleInfo = Any


def scan_registry_decorators(path: str,
                             module_importer: Type[Callable[[str], ModuleType]],
                             package_walker: Type[Callable[[str], Iterator[ModuleInfo]]]
                             ) -> None:
    """
    Imports all modules at package root 'path', forcing the registration
    decorators to populate the registry with application components and
    their associated metadata.
    :param path:
    :param module_importer:
    :param package_walker:
    :return:
    """
    package = module_importer(path)
    for _finder, name, _is_pkg in package_walker(package.__path__):
        module_name = package.__name__ + '.' + name
        module_importer(module_name)
        print(f"Imported component {module_name}")


def _get_factory_name_for_class(cls: type[Any]) -> str:
    return cls.__name__ + "Factory"


def _factory_loader(factory_name: str,
                    factory_package_path: str=FACTORY_PACKAGE_PATH,
                    importer: Callable[[str], ModuleType] = importlib.import_module,
                    ) -> Type[FactoryInterface]:
    factory_module = importer(factory_package_path)
    factory_cls = getattr(factory_module, factory_name)
    return factory_cls


def register_components_with_dependency_container(registry: dict[Type[Any], ComponentMetadata],
                                                  container: DependencyContainer,
                                                  loader: Callable[[str], Type[FactoryInterface]] = _factory_loader,
                                                  ) -> None:

    for _service_cls, metadata in registry.items():

        key = metadata.key
        factory_name = _get_factory_name_for_class(_service_cls)

        try:
            factory_cls = loader(factory_name)
            container.register_factory(key, lambda c=container, f=factory_cls: f(c).create())
            container.map_type_to_key(_service_cls, key)
            # Python uses late binding closure to resolve lambda functions, so a statement like
            # lambda: factory_cls(container)
            # will take the values from the outer scope at the time the lambda was called, not
            # when it was defined. This means every resolution with this key will use the
            # variables available at the time of the last iteration before it was called.
            # Here, we leverage the use of default values to capture the variables at the time
            # of definition, side-stepping this late-binding closure policy. Without them,
            # every resolution asked of the container would return an instance of the last
            # class in the iteration of this for loop. Using functools.partial is also
            # an acceptable solution.


        except AttributeError:
            print(f"Warning: No factory found for {_service_cls.__name__}. Expected {factory_name}.")

        except Exception as e:
            raise RuntimeError(f"Critical wiring failure for {_service_cls.__name__}: {e}") from e


def _sort_registry_items_by_lifecycle(registry: dict[Type[Any], ComponentMetadata]
                                      ) -> list[(Type[Any], ComponentMetadata)]:

    return sorted(
        registry.items(),
        key=lambda item: item[METADATA_INDEX]['lifecycle']
    )


def auto_register_components_with_dependency_container(registry: dict[Type[Any], ComponentMetadata],
                                                  container: DependencyContainer,
                                                  ) -> None:

    for _service_cls, metadata in registry.items():
        key = metadata.key

        try:
            container.register_class(key, _service_cls)

        except Exception as e:
            raise RuntimeError(f"Critical wiring failure for {_service_cls.__name__}: {e}") from e


def register_on_startup_components(registry: dict[Type[Any], ComponentMetadata],
                                   container: DependencyContainer,
                                   ) -> None:

    for _component_cls, metadata in registry.items():
        if metadata.register_at_startup:
            try:
                container.register_class(metadata.key, _component_cls)

            except Exception as e:
                raise RuntimeError(f"Critical wiring failure for {_component_cls.__name__}: {e}") from e


def get_metadata_by_key(key: str,
    registry: dict[Type[Any], ComponentMetadata],
    )-> ComponentMetadata | None:

    for metadata in registry.values():
        if metadata.key == key:
            return metadata

    return None


def register_dynamic_components(config_data: dict,
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

        container.register_controller_instance(
            key=component_name,
            cls=metadata.type,
            metadata=metadata
        )


def _get_lifecycle_components(registry: dict[Type[Any], ComponentMetadata]
                              ) -> dict[Type[Any], ComponentMetadata]:

    lifecycle_components = {
        _service_cls: metadata
        for _service_cls, metadata in registry.items()
        if metadata.lifecycle > 0
    }

    return lifecycle_components


def _sort_lifecycle_components(components: dict[type[Any], ComponentMetadata]
                               ) -> list[(type[Any], ComponentMetadata)]:

    sorted_lifecycle_components = sorted(
        components.items(),
        key=lambda item: item[METADATA_INDEX].lifecycle
    )

    return sorted_lifecycle_components


def register_components_with_lifecycle_manager(registry: dict[Type[Any], ComponentMetadata],
                                               container: DependencyContainer,
                                               manager: LifeCycleManager
                                               ) -> None:

    lifecycle_components = _get_lifecycle_components(registry)
    sorted_lifecycle_components = _sort_lifecycle_components(lifecycle_components)

    for _service_cls, metadata in sorted_lifecycle_components:
        key = metadata.key
        instance = container.resolve(key)
        manager.index_singleton(instance)


def register_components_with_lfm(container: DependencyContainer,
                                 manager: LifeCycleManager
                                 ) -> None:

    active_keys = container.get_registered_component_keys()

    for key in active_keys:
        metadata = container.get_metadata(key)
        if not metadata:
            continue
        if metadata.lifecycle > 0:
            component = container.resolve(key)
            manager.index_singleton(component)


def _interpolate_environment_variables(cfg: dict,
                                       env_loader: Callable[[str], str] = os.getenv,
                                       ) -> None:

    pattern=r"\${(.*?)}"
    re.compile(pattern)

    for key, val in cfg.items():
        if isinstance(val, dict):
            _interpolate_environment_variables(val, env_loader)
        elif isinstance(val, str):
            match = re.search(pattern, val)
            if match:
                env_var_name = match.group(1)
                env_val = env_loader(env_var_name)
                if env_val is None:
                    raise ValueError(f"{env_var_name} is not a valid environment variable.")
                else:
                    cfg[key] = env_val


def read_config(stream: IO[str],
                decoder: Callable[[IO[str]], dict] = load,
                parser: Callable[[dict], dict] = dict,
                ) -> Any:

    try:
        decoded = decoder(stream)
        parsed = parser(decoded)
    except Exception as e:
        raise RuntimeError(f"Critical failure reading config file: {e}") from e

    return parsed
