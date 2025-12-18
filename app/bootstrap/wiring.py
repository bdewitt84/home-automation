# app/bootstrap/wiring.py


from fastapi import FastAPI

from app.bootstrap.scanner import import_components, register_components_with_dependency_container, \
    register_components_with_lifecycle_manager
from app.di.registry import COMPONENT_METADATA_REGISTRY
from app.di.wiring import get_dependency_container, get_lifecycle_manager, register_settings, register_event_bus, \
    register_media_controller, register_media_service

SERVICE_PACKAGE_NAME = 'components'


def initialize_application(app: FastAPI) -> None:
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
    import_components(SERVICE_PACKAGE_NAME)
    register_components_with_dependency_container(COMPONENT_METADATA_REGISTRY, container)
    register_components_with_lifecycle_manager(COMPONENT_METADATA_REGISTRY, container, manager)

    # --- Register Component Singletons ---
    register_media_controller(container)

    # --- Register Service Singletons ---
    register_media_service(container)
