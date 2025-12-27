# app/bootstrap/wiring.py


from fastapi import FastAPI

import importlib
import pkgutil

from app.bootstrap.scanner import (
    scan_registry_decorators,
    register_components_with_dependency_container,
    register_components_with_lifecycle_manager,
)

from app.di.registry import COMPONENT_METADATA_REGISTRY

from app.di.wiring import (
    register_settings,
    register_event_bus,
    register_media_controller,
    register_media_service,
)

from app.bootstrap.state import (
    init_dependency_container,
    init_lifecycle_manager,
)

SERVICE_PACKAGE_NAME = 'components'


def bootstrap_application(app: FastAPI) -> None:
    """
    Registered the singletons with the dependency container
    :param app: FastAPI application
    :returns: None
    """
    container = init_dependency_container(app)
    manager = init_lifecycle_manager(app)

    # --- Register Application Singletons ---
    register_settings(container)
    register_event_bus(container)

    # --- Register Subprocess Singletons ---
    # register_vlc_process_manager(container)
    scan_registry_decorators(path=SERVICE_PACKAGE_NAME,
                             module_importer=importlib.import_module,
                             package_walker=pkgutil.walk_packages, )
    register_components_with_dependency_container(COMPONENT_METADATA_REGISTRY, container)
    register_components_with_lifecycle_manager(COMPONENT_METADATA_REGISTRY, container, manager)

    # --- Register Component Singletons ---
    register_media_controller(container)

    # --- Register Service Singletons ---
    register_media_service(container)
