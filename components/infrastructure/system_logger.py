# ./components/infrastructure/system_logger.py

from components.infrastructure.event_bus import ASyncEventBus
from events.logging import (
    LogEvent,
    LogLevel,
)


class SystemLogger:
    def __init__(self, bus: ASyncEventBus):
        self.bus = bus

    def info(self, msg, tags: list[str] = None):
        tags = tags or []

        self.bus.publish(
            LogEvent(level=LogLevel.INFO, message=msg, tags=tags,)
        )

    def warning(self, msg, tags: list[str] = None):
        tags = tags or []

        self.bus.publish(
            LogEvent(level=LogLevel.WARNING, message=msg, tags=tags)
        )

    def error(self, msg, tags: list[str] = None):
        tags = tags or []

        self.bus.publish(
            LogEvent(level=LogLevel.ERROR, message=msg, tags=tags)
        )

    def debug(self, msg, tags: list[str] = None):
        tags = tags or []

        self.bus.publish(
            LogEvent(level=LogLevel.DEBUG, message=msg, tags=tags)
        )
