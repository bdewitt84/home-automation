# components/infrastructure/os_utils.py

import subprocess

from app.di.registry import component
from app.models.system import SystemResult
from app.exceptions.system import SystemOperationError


@component(is_dependency=True)
class OSUtils:
    def __init__(self):
        pass

    def execute_shell_command(self, cmd: str) -> SystemResult:
        """
        :param cmd:
        :return:
        """

        try:
            completed_process = subprocess.run(cmd,
                                    shell=True,
                                    check=True,
                                    capture_output=True,
                                    text=True)

            system_result = SystemResult(
                command=cmd,
                output=completed_process.stdout.strip(),
                returncode=completed_process.returncode,
                success=True
            )

            return system_result

        except subprocess.CalledProcessError as e:
            raise SystemOperationError(f"Error executing shell command '{cmd}': {e}")

        except Exception as e:
            raise Exception(f"An unexpected error occurred executing cmd '{cmd}': {e}")
