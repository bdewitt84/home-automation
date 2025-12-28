# tests/test_container.py

import pytest

from unittest.mock import Mock

from app.di.container import DependencyContainer


def test_register_factory_success():
    container = DependencyContainer()
    mock_key = 'mock_key'
    mock_factory = Mock()

    container.register_factory(mock_key, mock_factory)

    assert container._factories[mock_key] == mock_factory


def test_register_factory_already_registered():
    container = DependencyContainer()
    mock_key = 'mock_key'
    mock_factory = Mock()
    container._factories[mock_key] = mock_factory

    with pytest.raises(ValueError):
        container.register_factory(mock_key, mock_factory)


def test_resolve_behavior():
    container = DependencyContainer()
    mock_key = 'mock_key'
    mock_instance = Mock()
    mock_factory = Mock(return_value=mock_instance)

    container.register_factory(mock_key, mock_factory)

    result_1 = container.resolve(mock_key)
    result_2 = container.resolve(mock_key)

    assert result_1 is mock_instance is result_2
    mock_factory.assert_called_once()


def test_resolve_recursive():
    container = DependencyContainer()

    class MockLeaf: pass
    class MockBranch:
        def __init__(self, root: MockLeaf): pass
    class MockRoot:
        def __init__(self, branch: MockBranch): pass

    leaf_key = 'leaf_key'
    branch_key = 'branch_key'
    root_key = 'root_key'

    container.register_class(leaf_key, MockLeaf)
    container.register_class(branch_key, MockBranch)
    container.register_class(root_key, MockRoot)

    result = container.resolve(root_key)

    assert isinstance(result, MockRoot)


def test_resolve_failure_not_registered():
    container = DependencyContainer()
    mock_key = 'mock_key'

    with pytest.raises(ValueError):
        container.resolve(mock_key)


def test_get_registered_component_keys():
    container = DependencyContainer()

    factory_keys = ['mock_key1', 'mock_key2', 'mock_key3']

    for key in factory_keys:
        container._factories[key] = Mock()

    result = container.get_registered_component_keys()

    for key in factory_keys:
        assert key in result


def test_get_constructor_requirements_success():

    container = DependencyContainer()

    class MockCls:
        def __init__(self, p1: str, p2: int): pass

    container.map_type_to_key(str, 'str_key')
    container.map_type_to_key(int, 'int_key')

    result = container._get_constructor_requirements(MockCls)

    expected = {
        'p1': str,
        'p2': int,
    }

    assert result == expected


def test_get_constructor_requirements_not_registered():
    container = DependencyContainer()

    class MockCls:
        def __init__(self, p1: str): pass

    with pytest.raises(ValueError) as e:
        container._get_constructor_requirements(MockCls)

    assert 'not registered' in str(e)


def test_get_constructor_requirements_no_annotation():

    container = DependencyContainer()

    class MockCls:
        def __init__(self, p1): pass

    with pytest.raises(ValueError) as e:
        container._get_constructor_requirements(MockCls)

    assert 'no annotation' in str(e)


def test_get_constructor_requirements_annotation_is_none():

    container = DependencyContainer()

    class MockCls:
        def __init__(self, p1: None): pass

    with pytest.raises(ValueError) as e:
        container._get_constructor_requirements(MockCls)

    assert 'None' in str(e)


def test_get_resolved_dependencies():
    container = DependencyContainer()
    class MockCls1: pass
    class MockCls2: pass
    container.map_type_to_key(MockCls1, 'MockCls1')
    container.map_type_to_key(MockCls2, 'MockCls2')
    container.register_factory('MockCls1', lambda: MockCls1())
    container.register_factory('MockCls2', lambda: MockCls2())

    requirements = {
        'p1': MockCls1,
        'p2': MockCls2,
    }

    result = container._get_resolved_dependencies(requirements)

    assert isinstance(result['p1'], MockCls1)
    assert isinstance(result['p2'], MockCls2)


def test_register_class():
    container = DependencyContainer()
    mock_key = 'mock_key'
    class MockCls: pass

    container.register_class(mock_key, MockCls)
    result = container.resolve(mock_key)

    assert isinstance(result, MockCls)


def test_map_type_to_key():
    container = DependencyContainer()

    class MockType: pass
    mock_key = 'mock_key'

    container.map_type_to_key(MockType, mock_key)

    assert container._type_registry[MockType] == mock_key
