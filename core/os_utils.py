# core/os_utils.py
import subprocess


def execute_shell_command(command: str) -> {}:
    """
    :param command:
    :return:
    """

    try:
        result = subprocess.run(command,
                               shell=True,
                               check=True,
                               capture_output=True,
                               text=True)
        return {
            "status": "success",
            "command": command,
            "stdout": result.stdout.strip(),
        }

    except subprocess.CalledProcessError as e:

        return {
            "status": "error",
            "command": command,
            "stderr": e.stderr.strip(),
            "returncode": e.returncode,
        }

    except Exception as e:

        return {
            "status": "fatal error",
            "message": str(e),
        }