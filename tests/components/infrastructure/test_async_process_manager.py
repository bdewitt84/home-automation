# ./tests/components/infrastructure/test_async_process_manager.py

import pytest
from unittest.mock import AsyncMock, Mock

from app.exceptions.system import (
    ProcessTerminationError,
    ProcessNotFoundError,
)
from app.models.process import ProcessHandle
from components.infrastructure.async_process_manager import AsyncProcessManager


@pytest.fixture
def process_runner():
    runner = AsyncMock()
    return runner


def generate_fake_handle(pid: int):
    return ProcessHandle(
        id=pid,
        process=Mock()
    )


@pytest.mark.asyncio
async def test_async_process_manager_spawn(process_runner):

    manager = AsyncProcessManager(process_runner)

    command = "command"
    args = [
        "arg_1",
        "arg_2",
    ]

    handle = AsyncMock()
    process_runner.run_process.return_value = handle

    result = await manager.spawn(
        command=command,
        args=args,
    )

    assert result == handle
    process_runner.run_process.assert_awaited_once_with(
        cmd=command,
        args=args,
    )


@pytest.mark.asyncio
async def test_async_process_manager_failed_to_start_process(process_runner):
    manager = AsyncProcessManager(process_runner)

    process_runner.run_process.side_effect = RuntimeError("Failed to start process")

    command = "command"
    args = [
        "arg_1",
        "arg_2",
    ]

    with pytest.raises(RuntimeError):
        await manager.spawn(command, args)


def test_async_process_manager_terminate(process_runner):
    manager = AsyncProcessManager(process_runner)

    fake_handle = generate_fake_handle(42)

    manager._processes[42] = fake_handle

    manager.terminate(42)
    fake_handle.process.terminate.assert_called_once() # type: ignore
    assert 42 not in manager._processes


def test_async_process_manager_terminate_pid_not_found(process_runner):
    manager = AsyncProcessManager(process_runner)

    with pytest.raises(ProcessNotFoundError):
        manager.terminate(42)


def test_async_process_manager_failed_to_terminate(process_runner):
    manager = AsyncProcessManager(process_runner)

    fake_handle = generate_fake_handle(42)
    manager._processes[42] = fake_handle

    fake_handle.process.terminate.side_effect = ProcessTerminationError("Fake Process Termination Error")

    with pytest.raises(ProcessTerminationError):
        manager.terminate(42)


@pytest.mark.asyncio
async def test_async_process_manager_stop(process_runner):
    manager = AsyncProcessManager(process_runner)

    fake_handle_1 = generate_fake_handle(41)
    fake_handle_2 = generate_fake_handle(42)

    manager._processes[42] = fake_handle_1
    manager._processes[43] = fake_handle_2

    await manager.stop()
    fake_handle_1.process.terminate.assert_called_once() # type: ignore
    fake_handle_2.process.terminate.assert_called_once() # type: ignore
