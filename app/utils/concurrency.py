# ./app/utils/concurrency.py


from asyncio import (
    Task,
    CancelledError,
)


class AsyncTaskHandle:
    def __init__(self, task: Task) -> None:
        self._task = task

    async def cancel(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except CancelledError:
                # this is the desired outcome, so we don't raise here
                pass
            finally:
                self._task = None
