# ./components/infrastructure/async_process_runner.py

from asyncio import (
    create_subprocess_exec,
    subprocess,
)
from typing import (
    IO,
    Protocol,
)

from app.di.registry import component
from app.models.process import ProcessHandle
from app.exceptions.system import ExecutableNotFoundError, ProcessStartupError


class SubProcessCreator(Protocol):
    async def __call__(self,
                 cmd:str,
                 *args:str,
                 stdin:int | IO | None = None,
                 stdout:int | IO | None = None,
                 stderr:int | IO | None = None,
                 ) -> subprocess.Process:
        ...


@component(is_dependency=True)
class AsyncProcessRunner:
    def __init__(self, create_subprocess: SubProcessCreator = create_subprocess_exec) -> None:
        self._create_subprocess = create_subprocess

    async def run_process(self, cmd: str, args: list[str|int] = None) -> ProcessHandle:
        effective_args = args if args else []
        try:
            process = await self._create_subprocess(
                cmd,
                *effective_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )

        except FileNotFoundError:
            raise ExecutableNotFoundError("Executable not found")

        except Exception as e:
            raise ProcessStartupError("Failed to start process") from e

        handle = ProcessHandle(
            id=process.pid,
            process=process
        )

        return handle
