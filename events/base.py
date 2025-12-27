# events/base.py

from pydantic import BaseModel
from datetime import datetime, timezone


class BaseEvent(BaseModel):

    time: datetime = datetime.now(timezone.utc)

    def get_type(self):
        return self.__class__.__name__
