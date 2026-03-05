# tests/test_scanner.py

from unittest.mock import Mock

from app.bootstrap.scanner import scan_for_components


def test_scan_for_components():

    path = "test_path"
    mock_pkg = Mock()
    mock_pkg.__path__ = ['mock/pkg/path']
    mock_pkg.__name__ = 'mock_pkg_name'
    mock_importer = Mock()
    mock_importer.side_effect = [mock_pkg, Mock()]

    mock_module_info = (None, 'mock_module', False)
    mock_walker = Mock(return_value=[mock_module_info])

    scan_for_components(path, mock_importer, mock_walker)

    mock_walker.assert_called_once_with(['mock/pkg/path'])
    mock_importer.assert_called_with('mock_pkg_name.mock_module')
