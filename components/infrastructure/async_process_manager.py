# ./components/infrastructure/async_process_manager.py

from app.di.registry import component
from app.models.process import ProcessHandle
from components.infrastructure.async_process_runner import AsyncProcessRunner
from app.exceptions.system import (
    ProcessTerminationError,
    ProcessNotFoundError,
)
from interfaces import LifecycleManagement


@component(is_dependency=True,
           lifecycle=0)
class AsyncProcessManager(LifecycleManagement):
    def __init__(self, async_process_runner: AsyncProcessRunner):
        self._runner = async_process_runner
        self._processes: dict[int, ProcessHandle] = {}

    async def spawn(self, command: str, args: list[str|int]) -> ProcessHandle:
        try:
            handle = await self._runner.run_process(
                cmd=command,
                args=args,
            )
        except Exception as e:
            raise RuntimeError("Failed to start process") from e
        self._processes[handle.id] = handle
        return handle

    def terminate(self, pid: int):
        try:
            handle = self._processes.pop(pid)
            handle.process.terminate()
        except KeyError:
            raise ProcessNotFoundError(f"Process with id {pid} not found")
        except Exception as e:
            raise ProcessTerminationError(f"Failed to terminate process with id {pid}") from e

    async def start(self):
        # todo: log startup
        pass

    async def stop(self):
        for pid in list(self._processes.keys()):
            self.terminate(pid=pid)
