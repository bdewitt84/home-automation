# app/bootstrap/wiring.py


from fastapi import FastAPI

import importlib
import pkgutil

from app.bootstrap.scanner import (
    scan_registry_decorators,
    register_dynamic_components,
    register_components_with_lfm,
    register_on_startup_components,
    load_config_from_disk,
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
CONFIG_FILE_PATH = './config/config.json'


def bootstrap_application(app: FastAPI) -> None:
    """
    Registered the singletons with the dependency container
    :param app: FastAPI application
    :returns: None
    """
    container = init_dependency_container(app)
    manager = init_lifecycle_manager(app)

    config_data = load_config_from_disk(CONFIG_FILE_PATH)

    # --- Register Application Singletons ---
    register_settings(container)
    register_event_bus(container)

    # --- Register Subprocess Singletons ---
    scan_registry_decorators(path=SERVICE_PACKAGE_NAME,
                             module_importer=importlib.import_module,
                             package_walker=pkgutil.walk_packages, )

    register_on_startup_components(COMPONENT_METADATA_REGISTRY, container)
    register_dynamic_components(config_data, container, COMPONENT_METADATA_REGISTRY)
    register_components_with_lfm(container, manager)

    # --- Register Component Singletons ---
    register_media_controller(container)

    # --- Register Service Singletons ---
    register_media_service(container)
