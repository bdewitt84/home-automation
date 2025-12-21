# tests/test_state.py

import pytest

from fastapi import FastAPI
from unittest.mock import Mock

from app.bootstrap.state import init_dependency_container, get_dependency_container
from app.bootstrap.state import init_lifecycle_manager, get_lifecycle_manager
from app.di.container import DependencyContainer
from app.lifecycle_manager import LifeCycleManager
from app.di.keys import CONTAINER_KEY, LIFECYCLE_MANAGER_KEY


def test_init_dependency_container():

    app = FastAPI()

    result = init_dependency_container(app)

    assert hasattr(app.state, CONTAINER_KEY)
    assert isinstance(getattr(app.state, CONTAINER_KEY), DependencyContainer)
    assert isinstance(result, DependencyContainer)


def test_init_lifecycle_manager():

    app = FastAPI()

    result = init_lifecycle_manager(app)

    assert hasattr(app.state, LIFECYCLE_MANAGER_KEY)
    assert isinstance(getattr(app.state, LIFECYCLE_MANAGER_KEY), LifeCycleManager)
    assert isinstance(result, LifeCycleManager)


def test_get_dependency_container():

    app = FastAPI()
    mock_container = Mock()
    setattr(app.state, CONTAINER_KEY, mock_container)

    result = get_dependency_container(app)

    assert result == mock_container


def test_get_lifecycle_manager():

    app = FastAPI()
    mock_manager = Mock()
    setattr(app.state, LIFECYCLE_MANAGER_KEY, mock_manager)

    result = get_lifecycle_manager(app)

    assert result == mock_manager
