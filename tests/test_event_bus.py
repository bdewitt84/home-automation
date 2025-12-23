# tests/test_event_bus.py
from time import sleep

import pytest
import pytest_asyncio
from unittest.mock import Mock, create_autospec

import asyncio

from components.infrastructure.event_bus import ASyncEventBus
from events.base import BaseEvent


def test_subscribe():

    bus = ASyncEventBus()

    class TestEvent(BaseEvent):
        pass
    mock_handler = Mock()

    bus.subscribe(TestEvent, mock_handler)

    # The event is in the subscribers dict
    assert TestEvent in bus._subscribers
    # The handler is subscribed to the event
    assert mock_handler in bus._subscribers[TestEvent]


async def test_publish():

    bus = ASyncEventBus()

    mock_event = create_autospec(BaseEvent)
    mock_event.__name__ = 'MockEvent'

    bus.publish(mock_event)

    # The queue has an event
    assert bus._queue.qsize() == 1
    event = await bus._queue.get()
    assert bus._queue.qsize() == 0
    # The event is the one that was published
    assert event == mock_event


async def test_bus_processes_event():

    bus = ASyncEventBus()

    mock_handler = Mock()

    bus.subscribe(BaseEvent, mock_handler)
    bus.publish(BaseEvent())
    await bus.start()
    await bus.wait_until_idle()

    # The handler that subscribes to the published event gets called
    mock_handler.assert_called_once()
