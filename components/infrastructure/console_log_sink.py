# ./components/infrastructure/console_log_sink.py

from typing import Callable, Any

from pydantic import BaseModel

from events.logging import LogEvent
from interfaces import LifecycleManagement
from components.infrastructure.event_bus import (
    ASyncEventBus,
    NotSubscribedError
)


class ConsoleLogSettings(BaseModel):
    log_level: int = 20


class ConsoleLogSink(LifecycleManagement):
    def __init__(self, event_bus: ASyncEventBus, settings:ConsoleLogSettings=ConsoleLogSettings(), output: Callable[[str], Any] = print) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._output = output

    async def start(self):
        self._event_bus.subscribe(
            event_type=LogEvent,
            handler=self._consume_log_event
        )

    async def stop(self):
        try:
            self._event_bus.unsubscribe(
                event_type=LogEvent,
                handler=self._consume_log_event
            )
        except NotSubscribedError:
            pass

    def _consume_log_event(self, event:LogEvent):
        if event.level >= self._settings.log_level:
            time_str = event.time.isoformat()
            str_out = f"[{time_str}] [LEVEL: {event.level}] {event.message}"
            self._output(str_out)
