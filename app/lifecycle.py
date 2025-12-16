# app.lifecycle.py

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

from typing import Type

from events.event_bus import ASyncEventBus

from app.di.keys import (
    EVENT_BUS_KEY, VLC_PROCESS_MANAGER_KEY,
)
from interfaces import LifecycleManagementInterface
import pkgutil
import importlib
from app.di.registry import COMPONENT_METADATA_REGISTRY

SERVICE_PACKAGE_NAME = 'components'


def _import_services(path):
    package = importlib.import_module(path)
    for _finder, name, _is_pkg in pkgutil.walk_packages(package.__path__):
        module_name = package.__name__ + '.' + name
        importlib.import_module(module_name)


def _register_services_with_dependency_container(registry, container: DependencyContainer):
    for _service_cls, metadata in registry.items():
        key = metadata['key']
        # factory: Type[FactoryInterface] = metadata['factory']
        factory_name = _service_cls.__name__ + 'Factory'
        factory_package_path = 'app.di.factories'
        factory_package = importlib.import_module(factory_package_path)
        factory_cls = getattr(factory_package, factory_name)

        container.register_singleton(key, lambda: factory_cls(container).create())


def _register_services_with_lifecycle_manager(registry, container: DependencyContainer, manager: LifeCycleManager):
    SERVICE_CLS_INDEX = 0
    METADATA_INDEX = 1

    sorted_registry_items = sorted(
        registry.items(),
        key=lambda item: item[METADATA_INDEX]['lifecycle']
    )
    for _service_cls, metadata in sorted_registry_items:
        if metadata['lifecycle'] > 0:
            key = metadata['key']
            instance = container.resolve(key)
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
    _import_services(SERVICE_PACKAGE_NAME)
    _register_services_with_dependency_container(COMPONENT_METADATA_REGISTRY, container)
    _register_services_with_lifecycle_manager(COMPONENT_METADATA_REGISTRY, container, manager)

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
    container = get_dependency_container(app)
    singleton_keys = container.get_registered_singleton_keys()

    for key in singleton_keys:
        instance = container.resolve(key)
        if isinstance(instance, LifecycleManagementInterface):
            await instance.start()


async def shutdown_state(app: FastAPI) -> None:
    """
    Stops all stoppable dependencies
    :param app: FastAPI application
    :returns: None
    """
    container = get_dependency_container(app)
    singleton_keys = container.get_registered_singleton_keys()

    for key in singleton_keys:
        instance = container.resolve(key)
        if isinstance(instance, LifecycleManagementInterface):
            await instance.stop()
