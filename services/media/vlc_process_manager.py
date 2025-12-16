# services/media/vlc_process_manager.py

from typing import Optional
import asyncio
from asyncio import StreamReader, create_subprocess_exec, subprocess
from interfaces import LifecycleManagementInterface
from app.di.registry import register_component_with_container
from app.di.keys import VLC_PROCESS_MANAGER_KEY


@register_component_with_container(key=VLC_PROCESS_MANAGER_KEY, lifecycle=100)
class VlcProcessManager(LifecycleManagementInterface):

    def __init__(self, host: str, port: str, password: str):
        self.host = host
        self.port = port
        self.password = password
        self._process: Optional[asyncio.subprocess.Process] = None


    async def _read_output_loop(self, stream: StreamReader):
        try:
            while True:
                line = await stream.readline()
                if not line:
                    break

                decoded_line = line.decode('utf-8').strip()
                if decoded_line:
                    # publish event here
                    print(f"[VLC-LOG]: {decoded_line}")

        except asyncio.CancelledError:
            # Expected when task is cancelled during shutdown
            pass
        except Exception as e:
            print('Error reading VLC output')
        finally:
            if self._process and self._process is None:
                await self._terminate_process()


    async def _terminate_process(self):

        if self._process and self._process.returncode is None:

            try:
                self._process.terminate()
                await asyncio.wait_for(self._process.wait(), timeout=5)

            except asyncio.TimeoutError:
                self._process.kill()
                await self._process.wait()

            except Exception as e:
                print(f"Failed to terminate VLC process: {e}")


    async def start(self):

        cmd = 'vlc'
        args = [
            r'-I', r'http',
            r'--http-host', self.host,
            r'--http-port', self.port,
            r'--http-password', self.password,
        ]
        try:
            self._process = await create_subprocess_exec(
                cmd,
                *args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            self._stdout_reader_task = asyncio.create_task(
                self._read_output_loop(self._process.stdout)
            )
        except FileNotFoundError:
            raise RuntimeError("VLC Executable not found")
        except Exception as e:
            raise RuntimeError("Failed to start VLC") from e


    async def stop(self):
        if self._stdout_reader_task:
            self._stdout_reader_task.cancel()

            try:
                await self._stdout_reader_task
            except asyncio.CancelledError:
                # this is the desired outcome, so we pass on this exception
                pass

        await self._terminate_process()
        print("VLC process stopped successfully")
