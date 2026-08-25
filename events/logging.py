# ./events/logging.py

from events.base import BaseEvent


class LogLevel:
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40


class LogEvent(BaseEvent):
        level: int
        message: str
        tags: list[str]
