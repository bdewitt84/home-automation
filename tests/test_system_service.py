# tests/test_system_service.py

from unittest.mock import patch
from components.services import system_service
from components.services.system_service import UPDATE_SCRIPT_PATH # We import the constant for clarity


OS_UTILS_MOCK_PATH = 'core.os_utils.execute_shell_command'


def test_update_application_success():
    """
    Tests that the update_application service function correctly calls the
    underlying OS utility with the system-wide update script command path.
    """

    mock_return = {
        "status": "success",
        "command": UPDATE_SCRIPT_PATH,
        "stdout": "git pull successful; restarting..."
    }

    with patch(OS_UTILS_MOCK_PATH, return_value=mock_return):

        result = system_service.update_application()

        assert result['status'] == "success"
        assert "success" in result['stdout']
        assert 'stderr' not in result


def test_update_application_failure():
    """
    Tests that the update_application service function handles and
    returns an error from the underlying OS utility.
    :return:
    """
    cmd = UPDATE_SCRIPT_PATH

    mock_return = {
        "status": "error",
        "command": cmd,
        "stdout": "git pull failed; restarting...",
        "stderr": "error message",
    }

    with patch(OS_UTILS_MOCK_PATH, return_value=mock_return) as mock_run:
        result = system_service.update_application()
        assert result['status'] == "error"
        assert 'stderr' in result
        mock_run.assert_called_once_with(cmd)
