# ./app/models/system.py

from pydantic import BaseModel


class SystemResult(BaseModel):
    command: str
    output: str
    success: bool
    returncode: int
