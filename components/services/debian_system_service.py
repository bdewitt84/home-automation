# components/debian_system_service.py

import os

from components.infrastructure.os_utils import OSUtils
from config.project import PROJECT_ROOT
from interfaces import SystemService


UPDATE_SCRIPT_RELATIVE_PATH = "./scripts/home-automation-update.sh"
COMMAND_REBOOT = "sudo reboot"
COMMAND_SHUTDOWN = "sudo shutdown"


class DebianSystemService(SystemService):
    def __init__(self, os_utils: OSUtils):
        super().__init__()
        self.os_utils = os_utils

    def reboot(self):
        cmd = COMMAND_REBOOT
        return self.os_utils.execute_shell_command(cmd)

    def shutdown(self):
        cmd = COMMAND_SHUTDOWN
        return self.os_utils.execute_shell_command(cmd)

    def update_application(self) -> dict:
        # TODO: incorporate path ops to OSUtils service
        cmd = os.path.join(PROJECT_ROOT, UPDATE_SCRIPT_RELATIVE_PATH)
        return self.os_utils.execute_shell_command(cmd)
