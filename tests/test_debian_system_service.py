# tests/test_debian_system_service.py

from unittest.mock import Mock
from components.services.debian_system_service import (
    DebianSystemService,
    UPDATE_SCRIPT_RELATIVE_PATH, # We import the constant for clarity
)

OS_UTILS_MOCK_PATH = 'core.os_utils.execute_shell_command'


def test_update_application_success():
    """
    Tests that the update_application service function correctly calls the
    underlying OS utility with the system-wide update script command path.
    """

    # Arrange
    mock_return = {
        "status": "success",
        "command": UPDATE_SCRIPT_RELATIVE_PATH,
        "stdout": "git pull successful; restarting..."
    }
    mock_os_utils = Mock()
    mock_os_utils.execute_shell_command.return_value = mock_return
    system_service = DebianSystemService(mock_os_utils)

    # Act
    result = system_service.update_application()

    #Assert
    assert result['status'] == "success"
    assert "success" in result['stdout']
    assert 'stderr' not in result


def test_update_application_failure():
    """
    Tests that the update_application service function handles and
    returns an error from the underlying OS utility.
    :return:
    """

    cmd = UPDATE_SCRIPT_RELATIVE_PATH

    mock_return = {
        "status": "error",
        "command": cmd,
        "stdout": "git pull failed; restarting...",
        "stderr": "error message",
    }
    mock_os_utils = Mock()
    mock_os_utils.execute_shell_command.return_value = mock_return
    system_service = DebianSystemService(mock_os_utils)

    # Act
    result = system_service.update_application()

    # Assert
    assert result['status'] == "error"
    assert 'stderr' in result
    assert any(cmd in arg for arg in mock_os_utils.execute_shell_command.call_args.args)
