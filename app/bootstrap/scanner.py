# app/bootstrap/scanner.py

import importlib
from typing import Type, Any
import pkgutil

from app.di.container import DependencyContainer
from app.di.registry import ComponentMetadata
from app.lifecycle_manager import LifeCycleManager


def import_components(path):
    package = importlib.import_module(path)
    for _finder, name, _is_pkg in pkgutil.walk_packages(package.__path__):
        module_name = package.__name__ + '.' + name
        importlib.import_module(module_name)
        print(f"Imported component {module_name}")


def register_components_with_dependency_container(registry: dict[Type[Any], ComponentMetadata],
                                                   container: DependencyContainer):
    for _service_cls, metadata in registry.items():
        key = metadata['key']

        factory_name = _service_cls.__name__ + 'Factory'
        factory_package_path = 'app.di.factories'

        try:
            factory_package = importlib.import_module(factory_package_path)
            factory_cls = getattr(factory_package, factory_name)
            # Python uses late binding closure to resolve lambda functions, so an statment like
            # labmda: factory_cls(container)
            # will take the values from the outer scope at the time the lambda was called, not
            # when it was defined. This means every resolution with this key will use the
            # variables available at the time of the last iteration before it was called.
            # Here, we leverage the use of default values to capture the variables at the time
            # of definition, side-stepping this late-binding closure policy. Without them,
            # every resolution asked of the container would return an instance of the last
            # class in the iteration of this for loop. Using functools.partial is also
            # an acceptable solution.
            container.register_singleton(key, lambda c=container, f=factory_cls: f(c).create())
            print(f"Imported {factory_cls.__name__} from {factory_package.__name__}")

        except AttributeError:
            print(f"⚠️ Warning: No factory found for {_service_cls.__name__}. Expected {factory_name}.")

        except Exception as e:
            raise RuntimeError(f"Critical wiring failure for {_service_cls.__name__}: {e}") from e


def register_components_with_lifecycle_manager(registry: dict[Type[Any], ComponentMetadata],
                                                container: DependencyContainer,
                                                manager: LifeCycleManager):
    SERVICE_CLS_INDEX = 0
    METADATA_INDEX = 1

    sorted_registry_items = sorted(
        registry.items(),
        key=lambda item: item[METADATA_INDEX]['lifecycle']
    )

    print(
        f"Asking lifecycle manager to process registry: {[item[SERVICE_CLS_INDEX].__name__ for item in sorted_registry_items]}")

    for _service_cls, metadata in sorted_registry_items:
        if metadata['lifecycle'] > 0:
            key = metadata['key']
            instance = container.resolve(key)
            print(f"Asking lifecycle manager to index {instance.__class__.__name__}")
            manager.index_singleton(instance)

