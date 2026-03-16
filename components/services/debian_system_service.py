# components/debian_system_service.py
import os

from core import os_utils
from config.project import PROJECT_ROOT
from interfaces import SystemService
import subprocess


UPDATE_SCRIPT_RELATIVE_PATH = "./scripts/home-automation-update.sh"
COMMAND_REBOOT = "sudo reboot"
COMMAND_SHUTDOWN = "sudo shutdown"


class DebianSystemService(SystemService):
    def __init__(self):
        super(DebianSystemService, self).__init__()

    def _execute_shell_command(self, cmd: str) -> dict:
        """
        :param cmd:
        :return:
        """

        try:
            result = subprocess.run(cmd,
                                    shell=True,
                                    check=True,
                                    capture_output=True,
                                    text=True)
            return {
                "status": "success",
                "command": cmd,
                "stdout": result.stdout.strip(),
            }

        except subprocess.CalledProcessError as e:

            return {
                "status": "error",
                "command": cmd,
                "stderr": e.stderr.strip(),
                "returncode": e.returncode,
            }

        except Exception as e:

            return {
                "status": "fatal error",
                "message": str(e),
            }

    def reboot(self):
        cmd = COMMAND_REBOOT
        return self._execute_shell_command(cmd)

    def shutdown(self):
        cmd = COMMAND_SHUTDOWN
        return self._execute_shell_command(cmd)

    def update_application(self) -> dict:
        """
        Executes application update script
        :return:
        """
        cmd = os.path.join(PROJECT_ROOT, UPDATE_SCRIPT_RELATIVE_PATH)
        return os_utils.execute_shell_command(cmd)
