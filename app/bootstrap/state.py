# app/bootstrap/state.py

from fastapi import FastAPI

from app.di.container import DependencyContainer
from app.di.keys import CONTAINER_KEY, LIFECYCLE_MANAGER_KEY
from app.lifecycle_manager import LifeCycleManager


def init_dependency_container(app: FastAPI) -> DependencyContainer:
    dependency_container = DependencyContainer()
    setattr(app.state, CONTAINER_KEY, dependency_container)
    return dependency_container


def init_lifecycle_manager(app: FastAPI) -> LifeCycleManager:
    lifecycle_manager = LifeCycleManager()
    setattr(app.state, LIFECYCLE_MANAGER_KEY, lifecycle_manager)
    return lifecycle_manager


def get_dependency_container(app: FastAPI) -> DependencyContainer:
    """
    Get dependency container from application state. Container is initialized
    in app.main.py
    :param app: FastAPI application
    :returns: dependency container
    """
    container: DependencyContainer = getattr(app.state, CONTAINER_KEY)
    return container


def get_lifecycle_manager(app: FastAPI) -> LifeCycleManager:
    manager: LifeCycleManager = getattr(app.state, LIFECYCLE_MANAGER_KEY)
    return manager
