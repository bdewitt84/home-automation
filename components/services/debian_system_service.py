# components/debian_system_service.py

import os

from components.infrastructure.os_utils import OSUtils
from config.project import PROJECT_ROOT
from interfaces import SystemService
from app.models.system import SystemResult

UPDATE_SCRIPT_RELATIVE_PATH = "./scripts/home-automation-update.sh"
COMMAND_REBOOT = "sudo reboot"
COMMAND_SHUTDOWN = "sudo shutdown"


class DebianSystemService(SystemService):
    def __init__(self, os_utils: OSUtils):
        super().__init__()
        self.os_utils = os_utils

    def reboot(self) -> SystemResult:
        cmd = COMMAND_REBOOT
        system_result: SystemResult = self.os_utils.execute_shell_command(cmd)
        return system_result

    def shutdown(self) -> SystemResult:
        cmd = COMMAND_SHUTDOWN
        return self.os_utils.execute_shell_command(cmd)

    def update_application(self) -> SystemResult:
        # TODO: incorporate path ops to OSUtils service
        cmd = os.path.join(PROJECT_ROOT, UPDATE_SCRIPT_RELATIVE_PATH)
        return self.os_utils.execute_shell_command(cmd)
