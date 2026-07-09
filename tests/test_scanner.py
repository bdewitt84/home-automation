# tests/test_scanner.py

from unittest.mock import Mock
import pytest
import sys

from app.bootstrap.scanner import Scanner


TEST_MODULE_PREFIX = 'tests.fixtures.scanner_dummy'


@pytest.fixture
def clean_dummy_modules():

    # Yield control to the test
    yield

    # Run cleanup when it's done, even if it raises
    dummy_prefix = TEST_MODULE_PREFIX
    modules_to_delete = [
        mod for mod in sys.modules if mod.startswith(dummy_prefix)
    ]

    for mod in modules_to_delete:
        del sys.modules[mod]


@pytest.fixture
def mock_importer():
    importer = Mock()
    fake_package = Mock()
    fake_package.__name__ = "components"
    fake_package.__path__ = ["/fake/os/path/components"]

    importer.return_value = fake_package
    return importer


@pytest.fixture
def mock_walker():
    walker = Mock()
    # Return a list of tuples mimicking (finder, name, is_pkg)
    # The scanner only extracts the middle element (name)
    walker.return_value = [
        (None, "components.infrastructure.event_bus", False),
        (None, "components.services.media", True),
    ]
    return walker


@pytest.fixture
def scanner(mock_walker, mock_importer):
    return Scanner(
        package_walker=mock_walker,
        module_importer=mock_importer
    )


def test_add_modules_to_scanned_modules(scanner):
    scanner._scanned_modules = []
    scanner._add_modules(["module1", "module2"])
    assert scanner._scanned_modules == ["module1", "module2"]


def test_clear_scanned_modules(scanner):
    scanner._scanned_modules = ["module1", "module2"]
    scanner.clear()
    assert scanner._scanned_modules == []


def test_scanner_scan_packages(scanner, mock_walker, mock_importer):
    paths = ['components']

    result = scanner.scan_packages(paths)

    # Mock walker's assigned returns
    assert result == [
        "components.infrastructure.event_bus",
        "components.services.media"
    ]

    mock_importer.assert_called_once_with('components')
    mock_walker.assert_called_once_with(
        ["/fake/os/path/components"],
        "components."
    )


def test_scanner_import_scanned_modules(scanner, mock_walker, mock_importer):
    scanner._scanned_modules = [
        "components.infrastructure.event_bus",
        "components.services.media"
    ]

    scanner.import_scanned_modules()

    mock_importer.assert_any_call("components.infrastructure.event_bus")
    mock_importer.assert_any_call("components.services.media")


def test_scanner_scan_real_packages():
    scanner = Scanner()
    paths = [TEST_MODULE_PREFIX]
    result = scanner.scan_packages(paths)
    assert TEST_MODULE_PREFIX + '.root_component' in result
    assert TEST_MODULE_PREFIX + '.nested.deep_component' in result


def test_scanner_import_real_modules(clean_dummy_modules):
    scanner = Scanner()
    modules = [TEST_MODULE_PREFIX + '.root_component',
               TEST_MODULE_PREFIX + '.nested.deep_component']
    scanner._add_modules(modules)

    assert TEST_MODULE_PREFIX + '.root_component' not in sys.modules
    assert TEST_MODULE_PREFIX + '.nested.deep_component' not in sys.modules

    scanner.import_scanned_modules()

    assert TEST_MODULE_PREFIX + '.root_component' in sys.modules
    assert TEST_MODULE_PREFIX + '.nested.deep_component' in sys.modules


@pytest.mark.integration
def test_scanner_scan_and_import_real_modules(clean_dummy_modules):
    scanner = Scanner()
    paths = [TEST_MODULE_PREFIX]
    scanned = scanner.scan_packages(paths)

    assert TEST_MODULE_PREFIX + '.root_component' not in sys.modules
    assert TEST_MODULE_PREFIX + '.nested.deep_component' not in sys.modules

    scanner.import_scanned_modules()

    assert TEST_MODULE_PREFIX + '.root_component' in scanned
    assert TEST_MODULE_PREFIX + '.nested.deep_component' in scanned
    assert TEST_MODULE_PREFIX + '.root_component' in sys.modules
    assert TEST_MODULE_PREFIX + '.nested.deep_component' in sys.modules
