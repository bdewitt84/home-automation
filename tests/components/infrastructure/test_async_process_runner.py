# ./tests/components/infrastructure/test_async_process_runner.py

import pytest
from unittest.mock import AsyncMock, ANY

from app.exceptions.system import ExecutableNotFoundError, ProcessStartupError
from components.infrastructure.async_process_runner import AsyncProcessRunner


@pytest.fixture
def mock_subprocess_creator():
    creator = AsyncMock()
    return creator


@pytest.mark.asyncio
async def test_asynch_process_runner(mock_subprocess_creator) -> None:

    runner = AsyncProcessRunner(create_subprocess=mock_subprocess_creator)
    cmd = "fake_cmd"
    args = ["arg1", "arg2"]

    await runner.run_process(cmd, args)

    mock_subprocess_creator.assert_awaited_once_with(cmd, *args, stdin=ANY, stdout=ANY)


@pytest.mark.asyncio
async def test_async_process_runner_async_file_not_found(mock_subprocess_creator) -> None:

    runner = AsyncProcessRunner(create_subprocess=mock_subprocess_creator)
    cmd = "fake_cmd"
    args = ["arg1", "arg2"]

    mock_subprocess_creator.side_effect = FileNotFoundError("File not found")

    with pytest.raises(ExecutableNotFoundError):
        await runner.run_process(cmd, args)


@pytest.mark.asyncio
async def test_async_process_unknown_exception(mock_subprocess_creator) -> None:

    runner = AsyncProcessRunner(create_subprocess=mock_subprocess_creator)
    cmd = "fake_cmd"
    args = ["arg1", "arg2"]

    mock_subprocess_creator.side_effect = Exception("An exception occurred")

    with pytest.raises(ProcessStartupError):
        await runner.run_process(cmd, args)
