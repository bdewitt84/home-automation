# ./components/infrastructure/async_stream_reader_factory.py

from asyncio import (
    StreamReader,
    CancelledError,
    create_task,
)
from typing_extensions import Protocol

from app.di.registry import component
from app.utils.concurrency import AsyncTaskHandle


class Callback(Protocol):
    def __call__(self, line: str) -> None: ...


@component(is_dependency=True)
class AsyncStreamReaderFactory:
    async def create(self, stream: StreamReader, callback: Callback):
        task = create_task(
            self._read_output_loop(stream, callback)
        )
        return AsyncTaskHandle(task)

    @staticmethod
    async def _read_output_loop(stream: StreamReader, callback: Callback):
        try:
            while True:
                line = await stream.readline()
                if not line:
                    break

                decoded_line = line.decode('utf-8').strip()
                if decoded_line:
                    callback(decoded_line)

        except CancelledError:
            # Expected when task is cancelled during shutdown
            pass

        except Exception as e:
            print(f'Error reading VLC output: {e}')
