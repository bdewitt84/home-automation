# tests/test_scanner.py

from unittest.mock import Mock, create_autospec, call

import pytest
import pytest_asyncio

from inspect import signature

from types import ModuleType

from app.bootstrap.scanner import (
    scan_registry_decorators,
    _get_factory_name_for_class,
    _factory_loader,
    register_components_with_dependency_container,
    auto_register_components_with_dependency_container,
    _get_lifecycle_components,
    _sort_lifecycle_components,
    register_components_with_lifecycle_manager,
)
from app.di.container import DependencyContainer
from app.di.registry import ComponentMetadata
from app.lifecycle_manager import LifeCycleManager
from interfaces import FactoryInterface


def test_scan_registry_decorators():

    mock_package = Mock()
    mock_package_name = 'mock_package'
    mock_package.__name__ = mock_package_name
    mock_package.__path__ = 'mock_package_path'

    mock_module_importer = Mock()
    mock_module_importer.return_value = mock_package

    mock_package_walker = Mock()
    mock_module_1_name = 'mock_module_1'
    mock_module_2_name = 'mock_module_2'
    mock_package_walker.return_value = [
        (False, mock_module_1_name, False),
        (False, mock_module_2_name, False),
    ]

    scan_registry_decorators(mock_package_name,
                             mock_module_importer,
                             mock_package_walker, )

    mock_module_importer.assert_any_call(f"{mock_package_name}.{mock_module_1_name}")
    mock_module_importer.assert_any_call(f"{mock_package_name}.{mock_module_2_name}")


def test_get_factory_name_for_class():
    class MockClass: pass
    expected_name = 'MockClassFactory'

    result = _get_factory_name_for_class(MockClass)

    assert result == expected_name


def test_factory_loader():

    mock_factory_name = 'mock_factory_name'
    mock_factory_package_path = 'mock_factory_package_path'

    mock_factory = create_autospec(FactoryInterface)

    mock_module: ModuleType = Mock()
    setattr(mock_module, mock_factory_name, mock_factory)

    def importer(name: str): return mock_module

    result = _factory_loader(mock_factory_name,
                             mock_factory_package_path,
                             importer)

    assert result is mock_factory


def test_register_components_with_dependency_container():

    mock_key = 'mock_key'
    class TestComponent1: pass
    mock_metadata_1 = ComponentMetadata(mock_key, 100)

    mock_registry = {TestComponent1: mock_metadata_1}

    mock_factory_instance = create_autospec(FactoryInterface)
    mock_factory_instance.create = Mock(return_value = TestComponent1())

    mock_factory_cls = Mock(return_value=mock_factory_instance)
    mock_loader = Mock(return_value=mock_factory_cls)

    mock_container = create_autospec(DependencyContainer)

    register_components_with_dependency_container(mock_registry,
                                                  mock_container,
                                                  mock_loader,)

    captured_lambda = mock_container.register_factory.call_args[0][1]

    result = captured_lambda()

    assert isinstance(result, TestComponent1)
    mock_factory_cls.assert_called_once_with(mock_container)
    mock_factory_instance.create.assert_called_once()


def test_auto_register_components_with_dependency_container():

    mock_container = create_autospec(DependencyContainer)

    class TestComponent1: pass
    mock_key = 'mock_key'
    mock_metadata_1 = ComponentMetadata(mock_key, 100)
    mock_registry = {TestComponent1: mock_metadata_1}

    auto_register_components_with_dependency_container(mock_registry,
                                                       mock_container)

    mock_container.register_class.assert_called_once_with(mock_key, TestComponent1)


def test_get_lifecycle_components():

    mock_key_has_lifecycle = 'mock_key_has_lifecycle'
    class TestComponentHasLifecycle: pass
    mock_metadata_has_lifecycle = ComponentMetadata(mock_key_has_lifecycle, 100)
    mock_key_no_lifecycle = 'mock_key_no_lifecycle'
    class TestComponentNoLifecycle: pass
    mock_metadata_no_lifecycle = ComponentMetadata(mock_key_no_lifecycle, 0)

    mock_registry = {
        TestComponentHasLifecycle: mock_metadata_has_lifecycle,
        TestComponentNoLifecycle: mock_metadata_no_lifecycle,
    }

    result = _get_lifecycle_components(mock_registry)

    assert TestComponentHasLifecycle in result
    assert TestComponentNoLifecycle not in result


def test_sort_lifecycle_components():
    mock_key_a = 'mock_key_a'
    class TestComponentA: pass
    mock_metadata_a = ComponentMetadata(mock_key_a, 100)
    mock_key_b = 'mock_key_b'
    class TestComponentB: pass
    mock_metadata_b = ComponentMetadata(mock_key_b, 200)

    mock_registry = {
        TestComponentB: mock_metadata_b,
        TestComponentA: mock_metadata_a,
    }

    result = _sort_lifecycle_components(mock_registry)

    assert result == [(TestComponentA, mock_metadata_a), (TestComponentB, mock_metadata_b)]


def test_register_components_with_lifecycle_manager():

    mock_key_a = 'mock_key_a'
    class TestComponentA: pass
    mock_metadata_a = ComponentMetadata(mock_key_a, 100)
    mock_key_b = 'mock_key_b'
    class TestComponentB: pass
    mock_metadata_b = ComponentMetadata(mock_key_b, 200)

    mock_registry = {
        TestComponentB: mock_metadata_b,
        TestComponentA: mock_metadata_a,
    }

    mock_lifecycle_manager = create_autospec(LifeCycleManager)
    mock_container: DependencyContainer = create_autospec(DependencyContainer)
    test_instance_a = TestComponentA()
    test_instance_b = TestComponentB()
    mock_container.resolve.side_effect = [test_instance_a, test_instance_b]

    register_components_with_lifecycle_manager(mock_registry, mock_container, mock_lifecycle_manager)

    call_order = [call(test_instance_a), call(test_instance_b)]
    mock_lifecycle_manager.index_singleton.assert_has_calls(call_order, any_order=False)
