# tests/test_core.py

from core import os_utils
import subprocess
from unittest.mock import patch


MOCK_SUBPROCESS_RUN_PATH = "core.os_utils.subprocess.run"

def test_execute_shell_command_success():
    """
    Tests that the execute_shell_command utility function correctly
    calls subprocess.run and returns the expected elements of the
    completed process.
    :return:
    """

    mock_completed_process = subprocess.CompletedProcess(
        args = "test_command",
        returncode = 0,
        stdout = "test_stdout\n",
        stderr = "",
    )

    with patch(MOCK_SUBPROCESS_RUN_PATH, return_value=mock_completed_process) as mock_run:
        result = os_utils.execute_shell_command("test_command")

        assert result["status"] == "success"
        assert result["stdout"] == "test_stdout" # checks stripping
        mock_run.assert_called_once()


def test_execute_shell_command_failure():
    """
    Tests that the execute_shell_command utility handles and returns
    errors from the OS
    :return:
    """
    cmd = "bad_command"

    mock_process_error = subprocess.CalledProcessError(
        cmd = cmd,
        returncode = 1,
        stderr = "test_stderr",
    )

    with patch(MOCK_SUBPROCESS_RUN_PATH, side_effect=mock_process_error) as mock_run:
        result = os_utils.execute_shell_command(cmd)

        assert result["status"] == "error"
        assert 'stderr' in result
        assert 'returncode' != 0
        mock_run.assert_called_once()


    """
    WHEN WE GET BACK
    finish writing this test... DONE
    write commits.
    pull on server.
    smoke test.
    """