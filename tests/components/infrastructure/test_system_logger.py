# ./tests/components/infrastructure/test_system_logger.py

import pytest
from unittest.mock import Mock

from components.infrastructure.system_logger import SystemLogger
from events.logging import(
    LogLevel,
    LogEvent,
)


@pytest.fixture()
def mock_event_bus():
    return Mock()


def generate_log_event(level: int = LogLevel.DEBUG, message: str = "", tags: list[str] = None) -> LogEvent:
        return LogEvent(level=level,
                        message=message,
                        tags=tags or []
                        )


@pytest.mark.parametrize("log_level_str, expected_level", [
    ("debug", LogLevel.DEBUG),
    ("error", LogLevel.ERROR),
    ("warning", LogLevel.WARNING),
    ("info", LogLevel.INFO),
])
def test_system_logger(mock_event_bus, log_level_str, expected_level):
    logger = SystemLogger(bus=mock_event_bus)
    test_msg = "test_info"
    test_tags = ["test_tag"]

    method = getattr(logger, log_level_str)

    method(msg=test_msg, tags=test_tags)

    published_event = mock_event_bus.publish.call_args.args[0]
    assert isinstance(published_event, LogEvent)
    assert published_event.level == expected_level
    assert published_event.message == test_msg
