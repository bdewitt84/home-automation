# services/system_service.py

from core import os_utils

UPDATE_SCRIPT_PATH = "usr/local/bin/home-automation-update.sh"
COMMAND_REBOOT = "sudo reboot"

def update_application() -> {}:
    """
    Executes application update script
    :return:
    """
    cmd = UPDATE_SCRIPT_PATH
    return os_utils.execute_shell_command(cmd)
