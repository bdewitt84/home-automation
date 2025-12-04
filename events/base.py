# events/base.py

from pydantic import BaseModel
from datetime import datetime


class BaseEvent(BaseModel):

    time: datetime = datetime.now(datetime.UTC)

    def get_type(self):
        return self.__class__.__name__



