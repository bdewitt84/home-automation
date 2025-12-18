# app/lifecycle.py

from fastapi import FastAPI

from app.di.container import DependencyContainer
from app.di.lifecycle_manager import LifeCycleManager
from app.di.wiring import (
    get_dependency_container,
    get_lifecycle_manager,
    register_settings,
    register_event_bus,
    register_media_controller,
    register_media_service,
)

import pkgutil
import importlib
from app.di.registry import COMPONENT_METADATA_REGISTRY

SERVICE_PACKAGE_NAME = 'components'


def _import_components(path):
    package = importlib.import_module(path)
    for _finder, name, _is_pkg in pkgutil.walk_packages(package.__path__):
        module_name = package.__name__ + '.' + name
        importlib.import_module(module_name)
        print(f"Imported component {module_name}")


def _register_components_with_dependency_container(registry, container: DependencyContainer):
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

        except Exception as e:
            raise RuntimeError(f"Critical wiring failure for {_service_cls.__name__}: {e}") from e


def _register_components_with_lifecycle_manager(registry, container: DependencyContainer, manager: LifeCycleManager):
    SERVICE_CLS_INDEX = 0
    METADATA_INDEX = 1

    sorted_registry_items = sorted(
        registry.items(),
        key=lambda item: item[METADATA_INDEX]['lifecycle']
    )

    print(f"Asking lifecycle manager to process registry: {[item[SERVICE_CLS_INDEX].__name__ for item in sorted_registry_items]}")

    for _service_cls, metadata in sorted_registry_items:
        if metadata['lifecycle'] > 0:
            key = metadata['key']
            instance = container.resolve(key)
            print(f"Asking lifecycle manager to index {instance.__class__.__name__}")
            manager.index_singleton(instance)
            

def configure_state(app: FastAPI) -> None:
    """
    Registered the singletons with the dependency container
    :param app: FastAPI application
    :returns: None
    """

    container = get_dependency_container(app)
    manager = get_lifecycle_manager(app)

    # --- Register Application Singletons ---
    register_settings(container)
    register_event_bus(container)

    # --- Register Subprocess Singletons ---
    # register_vlc_process_manager(container)
    _import_components(SERVICE_PACKAGE_NAME)
    _register_components_with_dependency_container(COMPONENT_METADATA_REGISTRY, container)
    _register_components_with_lifecycle_manager(COMPONENT_METADATA_REGISTRY, container, manager)

    # --- Register Component Singletons ---
    register_media_controller(container)

    # --- Register Service Singletons ---
    register_media_service(container)


async def startup_state(app: FastAPI) -> None:
    """
    Starts all startable dependencies
    :param app: FastAPI application
    :returns: None
    """
    manager = get_lifecycle_manager(app)
    await manager.start_registered()


async def shutdown_state(app: FastAPI) -> None:
    """
    Stops all stoppable dependencies
    :param app: FastAPI application
    :returns: None
    """
    manager = get_lifecycle_manager(app)
    await manager.stop_registered()
