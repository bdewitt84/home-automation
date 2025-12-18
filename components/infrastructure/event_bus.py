import asyncio
from typing import Callable, Type, Any
from events.base import BaseEvent
from interfaces import LifecycleManagementInterface


EventHandler = Callable[[BaseEvent], Any]

class ASyncEventBus(LifecycleManagementInterface):
    def __init__(self):
        self._subscribers: dict[Type[BaseEvent], list[EventHandler]] = {}
        self._queue: asyncio.Queue[BaseEvent | None] = asyncio.Queue()
        self._processing_task: asyncio.Task | None = None

    def subscribe(self, event_type: Type[BaseEvent], handler: EventHandler) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(handler)

    def publish(self, event: BaseEvent) -> None:
        self._queue.put_nowait(event)

    async def process_events(self) -> None:

        while True:

            event = await self._queue.get()

            if event is None:
                break

            event_type = type(event)
            handlers = self._subscribers.get(event_type, [])

            for handler in handlers:
                asyncio.create_task(handler(event))

            self._queue.task_done()

    async def start(self) -> None:
        if not self._processing_task:
            self._processing_task = asyncio.create_task(self.process_events())

    async def stop(self) -> None:
        if self._processing_task:
            self._queue.put_nowait(None)
