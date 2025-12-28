# tests/test_scanner.py

from unittest.mock import Mock, create_autospec

import pytest
import pytest_asyncio
from pip._internal.resolution.resolvelib.factory import Factory

from app.bootstrap.scanner import scan_registry_decorators, register_components_with_dependency_container
from app.di.container import DependencyContainer
from app.di.registry import ComponentMetadata


def test_import_components():

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


def test_register_components_with_dependency_container():

    mock_key = 'mock_key'
    class TestComponent1: pass
    mock_metadata_1 = ComponentMetadata(mock_key, 100)

    mock_registry = {TestComponent1: mock_metadata_1}

    mock_factory_instance = create_autospec(Factory)
    mock_factory_instance.create = Mock(return_value = TestComponent1())

    mock_factory_cls = Mock(return_value=mock_factory_instance)
    mock_loader = Mock(return_value=mock_factory_cls)

    mock_container = DependencyContainer()

    register_components_with_dependency_container(mock_registry,
                                                  mock_container,
                                                  mock_loader,)


    keys = mock_container.get_registered_component_keys()

    assert mock_key in keys

    result = mock_container.resolve(mock_key)

    assert isinstance(result, TestComponent1)

    mock_factory_cls.assert_called_once_with(mock_container)
    mock_factory_instance.create.assert_called_once()
