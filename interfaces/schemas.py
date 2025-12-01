# interfaces/schemas.py

from pydantic import BaseModel


class MediaControlStatus(BaseModel):
    state: str = "N/A"
    volume: int = 0
    time: int = 0
    length: int = 0