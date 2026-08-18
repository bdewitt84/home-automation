# ./tests/utils/test_concurrency.py
import asyncio
import pytest

from app.utils.concurrency import AsyncTaskHandle


@pytest.mark.asyncio
async def test_stream_reader_handle() -> None:
    fake_task = asyncio.Future()
    reader = AsyncTaskHandle(fake_task) # type: ignore

    await reader.cancel()

    assert fake_task.cancelled()
    assert reader._task is None
