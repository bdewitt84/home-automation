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
        # If don't know about this event, create a list of handlers for it
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        # Add the handler to our subscribers list for this event
        self._subscribers[event_type].append(handler)

    def publish(self, event: BaseEvent) -> None:
        self._queue.put_nowait(event)

    async def process_events(self) -> None:

        while True:

            event = await self._queue.get()

            # Look for the sentinel value (None) and break if we find it
            if event is None:
                self._queue.task_done()
                break

            # Get any subscribing handlers for our event
            event_type = type(event)
            handlers = self._subscribers.get(event_type, [])

            if handlers:
                # Create a new task for each handler
                tasks = [
                    asyncio.create_task(self._safe_handle(handler, event))
                    for handler in handlers
                ]
                # Wait until all handlers are finished handling
                await asyncio.gather(*tasks)

            self._queue.task_done()

    async def _safe_handle(self, handler: EventHandler, event: BaseEvent) -> None:
        """Helper to ensure one failing handler doesn't silence errors."""
        try:
            result = handler(event)
            # If the handler is async, it returns a coroutine. We need
            # to await it for it to actually execute.
            if asyncio.iscoroutine(result):
                await result

        except Exception as e:
            print(f"EventBus: Handler {handler.__name__} failed for event {type(event).__name__}: {e}")

    async def start(self) -> None:
        if not self._processing_task:
            # Create an async task for our task processor to live in
            self._processing_task = asyncio.create_task(self.process_events())

    async def stop(self) -> None:
        if self._processing_task:
            self._queue.put_nowait(None)

        await self._queue.join()

    async def wait_until_idle(self):
        await self._queue.join()
