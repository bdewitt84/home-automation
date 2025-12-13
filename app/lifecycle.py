# app.lifecycle.py

from fastapi import FastAPI

from app.di.wiring import (
    get_dependency_container,
    register_settings,
    register_event_bus,
    start_event_bus,
    register_media_controller,
    register_media_service,
    register_vlc_process_manager,
    start_vlc_process_manager,
)

from events.event_bus import ASyncEventBus

from app.di.keys import (
    EVENT_BUS_KEY, VLC_PROCESS_MANAGER_KEY,
)

from services.media import VLCProcessManager


def configure_state(app: FastAPI) -> None:
    """
    Registered the singletons with the dependency container
    :param app: FastAPI application
    :returns: None
    """

    container = get_dependency_container(app)

    # --- Register Application Singletons ---
    register_settings(container)
    register_event_bus(container)

    # --- Register Subprocess Singletons ---
    register_vlc_process_manager(container)

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

    # --- Start event bus ---
    start_event_bus(container)

    # --- Start subprocesses ---
    await start_vlc_process_manager(container)


async def shutdown_state(app: FastAPI) -> None:
    """
    Stops all stoppable dependencies
    :param app: FastAPI application
    :returns: None
    """
    container = get_dependency_container(app)

    # --- Shut down bus ---
    bus:ASyncEventBus = container.resolve(EVENT_BUS_KEY)
    bus.stop()

    # --- Shut down VLC process ---
    vlc_process_manager = container.resolve(VLC_PROCESS_MANAGER_KEY)
    await vlc_process_manager.stop()
