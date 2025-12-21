# app/bootstrap/state.py

from fastapi import FastAPI

from app.di.container import DependencyContainer
from app.di.keys import CONTAINER_KEY, LIFECYCLE_MANAGER_KEY
from app.lifecycle_manager import LifeCycleManager


def create_dependency_container(app: FastAPI) -> None:
    dependency_container = DependencyContainer()
    setattr(app.state, CONTAINER_KEY, dependency_container)


def create_lifecycle_manager(app: FastAPI) -> None:
    lifecycle_manager = LifeCycleManager()
    setattr(app.state, LIFECYCLE_MANAGER_KEY, lifecycle_manager)
