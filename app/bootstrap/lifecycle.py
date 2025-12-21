# app/bootstrap/lifecycle.py

from fastapi import FastAPI

from app.bootstrap.state import get_lifecycle_manager


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
