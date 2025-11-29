# services/system_service.py
import os

from core import os_utils
from config.project import PROJECT_ROOT

UPDATE_SCRIPT_RELATIVE_PATH = "./scripts/home-automation-update.sh"
COMMAND_REBOOT = "sudo reboot"

def update_application() -> {}:
    """
    Executes application update script
    :return:
    """
    cmd = os.path.join(PROJECT_ROOT, UPDATE_SCRIPT_RELATIVE_PATH)
    return os_utils.execute_shell_command(cmd)
