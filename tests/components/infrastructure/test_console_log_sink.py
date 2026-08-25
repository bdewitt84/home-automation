# ./tests/components/infrastructure/test_console_log_sink.py

import pytest
from unittest.mock import (
    AsyncMock,
    Mock,
)
from events.logging import (
    LogLevel,
    LogEvent,
)
from components.infrastructure.console_log_sink import (
    ConsoleLogSink,
    ConsoleLogSettings,
)


@pytest.fixture()
def fake_console_settings():
    mock_settings = ConsoleLogSettings(log_level= LogLevel.DEBUG)
    return mock_settings


@pytest.fixture()
def mock_async_event_bus():
    return AsyncMock()


@pytest.fixture()
def mock_output():
    return Mock()


def generate_log_event(level: int = LogLevel.DEBUG, message: str = "", tags: list[str] = None) -> LogEvent:
    return LogEvent(level = level,
                    message = message,
                    tags = tags or []
                    )


def test_consume_log_event(fake_console_settings, mock_async_event_bus, mock_output):
    sink = ConsoleLogSink(settings=fake_console_settings,
                          event_bus=mock_async_event_bus,
                          output=mock_output)

    test_msg = 'test message'
    event = generate_log_event(message=test_msg)

    sink._consume_log_event(event)

    called_with = mock_output.call_args.args[0]
    assert f"[LEVEL: {event.level}]" in called_with
    assert event.message in called_with


def test_consumer_log_event_filters_level(fake_console_settings, mock_async_event_bus, mock_output):
    sink = ConsoleLogSink(settings=fake_console_settings,
                          event_bus=mock_async_event_bus,
                          output=mock_output)

    event = generate_log_event()
    fake_console_settings.log_level = LogLevel.ERROR

    sink._consume_log_event(event)

    mock_output.assert_not_called()


@pytest.mark.asyncio
async def test_start(fake_console_settings, mock_async_event_bus, mock_output):
    sink = ConsoleLogSink(settings=fake_console_settings,
                          event_bus=mock_async_event_bus,
                          output=mock_output)

    await sink.start()

    mock_async_event_bus.subscribe.assert_called_once_with(
        event_type=LogEvent,
        handler=sink._consume_log_event,
    )


@pytest.mark.asyncio
async def test_stop(fake_console_settings, mock_async_event_bus, mock_output):
    sink = ConsoleLogSink(settings=fake_console_settings,
                          event_bus=mock_async_event_bus,
                          output=mock_output)

    await sink.stop()

    mock_async_event_bus.unsubscribe.assert_called_once_with(
        event_type=LogEvent,
        handler=sink._consume_log_event,
    )
