# events/base.py

from pydantic import BaseModel, Field
from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc)

class BaseEvent(BaseModel):

    time: datetime = Field(default_factory=utc_now)

    def get_type(self):
        return self.__class__.__name__
