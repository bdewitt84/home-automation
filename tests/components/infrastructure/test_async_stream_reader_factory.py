# ./tests/components/infrastructure/test_async_stream_reader_factory.py

import pytest
from unittest.mock import Mock, AsyncMock

from app.utils.concurrency import AsyncTaskHandle
from components.infrastructure.async_stream_reader_factory import AsyncStreamReaderFactory


@pytest.fixture
def mock_stream():
    stream = AsyncMock()
    stream.readline.side_effect = [
        b"line 1\n",
        b"line 2\n",
        b""
    ]
    return stream


@pytest.fixture
def mock_callback():
    return Mock()


@pytest.mark.asyncio
async def test_async_stream_reader_factory(mock_stream, mock_callback):
    factory = AsyncStreamReaderFactory()

    reader = await factory.create(mock_stream, mock_callback)

    assert isinstance(reader, AsyncTaskHandle)
    await reader.cancel()


@pytest.mark.asyncio
async def test_read_output_loop(mock_stream, mock_callback):

    await AsyncStreamReaderFactory._read_output_loop(mock_stream, mock_callback)

    assert mock_callback.call_count == 2
    mock_callback.assert_any_call('line 1')
    mock_callback.assert_any_call('line 2')
