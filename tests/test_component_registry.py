# tests/test_component_registry.py

import pytest
from unittest.mock import Mock

from app.di.component_registry import ComponentRegistry
from app.exceptions.di import DuplicateKeyError
from app.models.component import ComponentMetadata


def _get_mock_component_data(key: str=None,
                             is_dependency: bool=False,
                             cls: type=None,
                             lifecycle: int=None,):
    # TODO: Consider taking arguments for key, possibly just stuffing it in metadata
    registry = ComponentRegistry()
    mock_factory = Mock()
    class MockComponent: pass
    mock_metadata = ComponentMetadata(
        key = key or MockComponent.__name__,
        type = cls or MockComponent,
        is_dependency = is_dependency,
        lifecycle = lifecycle or 0,
    )

    return registry, mock_factory, mock_metadata

def test_add_component_is_dependency():
    registry, mock_factory, mock_metadata = _get_mock_component_data(
        is_dependency=True
    )
    mock_type = mock_metadata.type
    mock_key = 'test'

    registry.add_component(mock_key, mock_factory, mock_metadata)

    assert registry.get_factory(mock_key) == mock_factory
    assert registry.get_metadata(mock_key) == mock_metadata
    assert registry.get_key_by_type(mock_type) == mock_key


def test_add_component_is_not_dependency():

    mock_key = 'test'
    registry, mock_factory, mock_metadata = _get_mock_component_data(key=mock_key)
    mock_type = mock_metadata.type

    registry.add_component(mock_key, mock_factory, mock_metadata)

    assert registry.is_dependency(mock_type) is False
    assert registry.get_key_by_type(mock_type) is None


def test_add_component_duplicate_key():
    registry, mock_factory_a, mock_metadata_a = _get_mock_component_data()
    _, mock_factory_b, mock_metadata_b = _get_mock_component_data()
    mock_key = 'test'
    registry.add_component(mock_key, mock_factory_a, mock_metadata_a)

    with pytest.raises(DuplicateKeyError) as e:
        registry.add_component(mock_key, mock_factory_b, mock_metadata_b)

    assert 'key' in str(e.value).lower()


def test_add_component_already_registered():
    registry, mock_factory, mock_metadata = _get_mock_component_data(is_dependency=True)
    registry.add_component('test_a', mock_factory, mock_metadata)
    with pytest.raises(DuplicateKeyError) as e:
        registry.add_component('test_b', mock_factory, mock_metadata)

    assert 'type' in str(e).lower()


def test_store_singleton():
    registry = ComponentRegistry()
    mock_singleton = Mock()
    mock_key = 'test'
    registry.store_singleton(mock_key, mock_singleton)

    assert mock_singleton in registry._singletons.values()


def test_get_singleton():
    registry = ComponentRegistry()
    mock_singleton = Mock()
    mock_key = 'test'
    registry._singletons[mock_key] = mock_singleton

    assert registry.get_singleton(mock_key) == mock_singleton


def test_get_factory_registered():
    registry, mock_factory, mock_metadata = _get_mock_component_data(is_dependency=True)
    mock_key = 'test'
    registry.add_component(mock_key, mock_factory, mock_metadata)

    assert registry.get_factory(mock_key) == mock_factory


def test_get_factory_not_registered():
    registry = ComponentRegistry()
    mock_key = 'test'

    result = registry.get_factory(mock_key)

    assert result is None


def test_get_metadata():
    registry, mock_factory, mock_metadata = _get_mock_component_data(is_dependency=True)
    mock_key = 'test'
    registry.add_component(mock_key, mock_factory, mock_metadata)

    result = registry.get_metadata(mock_key)

    assert result == mock_metadata


def test_get_key_by_type_registered():
    registry = ComponentRegistry()
    class MockComponent: pass
    mock_key = 'test'
    registry._type_to_key[MockComponent] = mock_key

    result = registry.get_key_by_type(MockComponent)

    assert result == mock_key


def test_get_key_by_type_not_registered():
    registry = ComponentRegistry()
    class MockComponent: pass

    assert registry.get_key_by_type(MockComponent) is None


def test_get_all_metadata():
    registry, mock_factory_a, mock_metadata_a = _get_mock_component_data()
    _, mock_factory_b, mock_metadata_b = _get_mock_component_data()
    registry.add_component('test_a', mock_factory_a, mock_metadata_a)
    registry.add_component('test_b', mock_factory_b, mock_metadata_b)

    result = registry.get_all_metadata().values()

    assert mock_metadata_a in result
    assert mock_metadata_b in result


def test_is_registered():
    registry, mock_factory_a, mock_metadata_a = _get_mock_component_data()
    mock_key_registered = 'true'
    mock_key_not_registered = 'false'
    registry.add_component(mock_key_registered, mock_factory_a, mock_metadata_a)

    assert registry.is_registered(mock_key_registered) is True
    assert registry.is_registered(mock_key_not_registered) is False


def test_is_dependency():

    class MockDependency: pass
    registry, mock_factory_a, mock_metadata_a = _get_mock_component_data(
        is_dependency=True,
        cls=MockDependency
    )

    class MockNotDependency: pass
    _, mock_factory_b, mock_metadata_b = _get_mock_component_data(
        is_dependency=False,
        cls=MockNotDependency
    )

    registry.add_component('test_a', mock_factory_a, mock_metadata_a)
    registry.add_component('test_b', mock_factory_b, mock_metadata_b)

    assert registry.is_dependency(MockDependency) is True
    assert registry.is_dependency(MockNotDependency) is False


def test_get_registered_keys():
    registry, mock_factory_a, mock_metadata_a = _get_mock_component_data()
    _, mock_factory_b, mock_metadata_b = _get_mock_component_data()
    mock_key_a = 'test_a'
    mock_key_b = 'test_b'
    registry.add_component(mock_key_a, mock_factory_a, mock_metadata_a)
    registry.add_component(mock_key_b, mock_factory_b, mock_metadata_b)

    result = registry.get_registered_keys()

    assert mock_key_a in result
    assert mock_key_b in result

def test_get_lifecycle_keys():

    mock_key_a = 'test_a'
    mock_key_b = 'test_b'
    mock_key_c = 'test_c'
    registry, mock_factory_a, mock_metadata_a = _get_mock_component_data(key=mock_key_a, lifecycle=2)
    _, mock_factory_b, mock_metadata_b = _get_mock_component_data(key=mock_key_b, lifecycle=1)
    _, mock_factory_c, mock_metadata_c = _get_mock_component_data(key=mock_key_c,lifecycle=0)
    registry.add_component(mock_key_a, mock_factory_a, mock_metadata_a)
    registry.add_component(mock_key_b, mock_factory_b, mock_metadata_b)
    registry.add_component(mock_key_c, mock_factory_c, mock_metadata_c)

    result = registry.get_lifecycle_keys()

    assert result == [mock_key_b, mock_key_a]
    assert mock_key_c not in result
