# components/infrastructure/os_utils.py

import subprocess

from app.di.registry import component


@component(is_dependency=True)
class OSUtils:
    def __init__(self):
        pass

    def execute_shell_command(self, cmd: str) -> dict:
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
