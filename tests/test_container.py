# tests/test_container.py

import pytest

from unittest.mock import Mock

from app.di.container import DependencyContainer


def test_register_singleton_success():
    container = DependencyContainer()
    mock_key = 'mock_key'
    mock_factory = Mock()

    container.register_singleton(mock_key, mock_factory)

    assert container._factories[mock_key] == mock_factory


def test_register_singleton_already_registered():
    container = DependencyContainer()
    mock_key = 'mock_key'
    mock_factory = Mock()
    container._factories[mock_key] = mock_factory

    with pytest.raises(ValueError):
        container.register_singleton(mock_key, mock_factory)


def test_resolve_singleton_behavior():
    container = DependencyContainer()
    mock_key = 'mock_key'
    mock_instance = Mock()
    mock_factory = Mock(return_value=mock_instance)

    container.register_singleton(mock_key, mock_factory)

    result_1 = container.resolve(mock_key)
    result_2 = container.resolve(mock_key)

    assert result_1 is mock_instance is result_2
    mock_factory.assert_called_once()


def test_resolve_failure_not_registered():
    container = DependencyContainer()
    mock_key = 'mock_key'

    with pytest.raises(ValueError):
        container.resolve(mock_key)


def test_get_registered_singleton_keys():
    container = DependencyContainer()

    factory_keys = ['mock_key1', 'mock_key2', 'mock_key3']

    for key in factory_keys:
        container._factories[key] = Mock()

    result = container.get_registered_singleton_keys()

    for key in factory_keys:
        assert key in result
