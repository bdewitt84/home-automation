# ./components/services/media/vlc_http_interface.py

from pydantic import BaseModel

from app.di.registry import component
from components.infrastructure.async_process_manager import AsyncProcessManager
from components.infrastructure.async_stream_reader_factory import (
    AsyncStreamReaderFactory,
    AsyncTaskHandle,
)
from app.exceptions.system import ProcessStartupError
from app.models.process import ProcessHandle


class NoReaderHandleError(Exception): pass


class NoProcessHandleError(Exception): pass


class VlcHttpInterfaceSettings(BaseModel):
    host: str='127.0.0.1'
    port: str='8080'
    password: str='your_password'


@component()
class VlcHttpInterface:
    def __init__(self,
                 settings: VlcHttpInterfaceSettings,
                 async_process_manager: AsyncProcessManager,
                 async_reader_factory: AsyncStreamReaderFactory, ):
        self._settings = settings
        self._async_process_manager = async_process_manager
        self._async_stream_consumer = async_reader_factory

        self._process_handle: ProcessHandle | None = None
        self._reader_handle: AsyncTaskHandle | None = None

    def _callback(self, line: str) -> None:
        print(line)

    async def start(self):
        if self._reader_handle:
            raise ProcessStartupError("Cannot start interface: "
                                      "Reader handle already exists. "
                                      "Hint: is the interface already started?")
        if self._process_handle:
            raise  ProcessStartupError("Cannot start interface: "
                                       "Process handle already exists. "
                                       "Hint: is the interface already started?")


        cmd = 'vlc'
        args = [
            r'-I', r'http',
            r'--http-host', self._settings.host,
            r'--http-port', self._settings.port,
            r'--http-password', self._settings.password,
        ]
        self._process_handle = await self._async_process_manager.spawn(
            command=cmd,
            args=args,
        )
        self._reader_handle = await self._async_stream_consumer.create(
            stream=self._process_handle.stdout,
            callback=self._callback,
        )

    async def stop(self):

        if self._reader_handle:
            try:
                await self._reader_handle.cancel()
            except Exception as e:
                # todo: implement logging
                print(f"Failed to cancel reader task: {e}")
            finally:
                self._reader_handle = None

        if self._process_handle:
            try:
                await self._async_process_manager.terminate(pid=self._process_handle.id)
            except Exception as e:
                # todo: implement logging
                print(f"Failed to cancel process task: {e}")
            finally:
                self._process_handle = None
