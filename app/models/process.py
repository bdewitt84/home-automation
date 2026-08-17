# ./app/models/process.py

from asyncio import StreamReader
from asyncio.subprocess import Process
from dataclasses import dataclass


@dataclass
class ProcessHandle:
    id: int
    process: Process

    @property
    def stdout(self) -> StreamReader:
        return self.process.stdout
