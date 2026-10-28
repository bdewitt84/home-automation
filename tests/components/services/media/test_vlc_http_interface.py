# ./tests/components/services/media/test_vlc_http_interface.py

import pytest
from unittest.mock import AsyncMock, Mock

from app.exceptions.system import ProcessStartupError
from components.infrastructure.async_process_manager import AsyncProcessManager
from components.infrastructure.async_stream_reader_factory import AsyncStreamReaderFactory
from components.infrastructure.system_logger import SystemLogger
from components.services.media.vlc_http_interface import (
    VlcHttpInterface,
    VlcHttpInterfaceSettings,
)


@pytest.fixture
def create_vlc_http_interface():

    def interface_factory(settings: VlcHttpInterfaceSettings = None,
                          async_process_manager: AsyncProcessManager = None,
                          async_reader_factory: AsyncStreamReaderFactory = None,
                          logger: SystemLogger = None
                          ):
        interface = VlcHttpInterface(
            settings=settings or VlcHttpInterfaceSettings(),
            async_process_manager=async_process_manager or AsyncMock(),
            async_reader_factory=async_reader_factory or AsyncMock(),
            logger=logger or Mock()
        )
        return interface

    return interface_factory


@pytest.mark.asyncio
async def test_vlc_http_interface_start(create_vlc_http_interface):
    mock_async_process_manager = AsyncMock()
    mock_async_reader_factory = AsyncMock()
    fake_settings = VlcHttpInterfaceSettings()
    interface = create_vlc_http_interface(
        settings=fake_settings,
        async_process_manager=mock_async_process_manager,
        async_reader_factory=mock_async_reader_factory,
    )
    cmd = 'vlc'
    args = [
        r'-I', r'http',
        r'--http-host', fake_settings.host,
        r'--http-port', fake_settings.port,
        r'--http-password', fake_settings.password,
    ]
    handle = Mock()
    mock_stdout = Mock()
    handle.stdout = mock_stdout
    mock_async_process_manager.spawn.return_value = handle

    await interface.start()

    mock_async_process_manager.spawn.assert_awaited_once_with(
        command=cmd,
        args=args,
    )
    mock_async_reader_factory.create.assert_awaited_once_with(
        stream=mock_stdout,
        callback=interface._callback,
    )


@pytest.mark.asyncio
async def test_vlc_http_interface_stop(create_vlc_http_interface):
    mock_async_process_manager = AsyncMock()
    interface = create_vlc_http_interface(
        async_process_manager=mock_async_process_manager
    )

    mock_reader_handle = AsyncMock()
    interface._reader_handle = mock_reader_handle

    mock_process_handle = AsyncMock()
    pid = 42
    mock_process_handle.id = pid
    interface._process_handle = mock_process_handle

    await interface.stop()

    mock_reader_handle.cancel.assert_awaited_once()
    mock_async_process_manager.terminate.assert_awaited_once_with(pid=pid)


@pytest.mark.asyncio
async def test_vlc_http_interface_start_reader_handle_exists(create_vlc_http_interface):
    interface = create_vlc_http_interface()

    mock_reader_handle = Mock()
    interface._reader_handle = mock_reader_handle

    with pytest.raises(ProcessStartupError):
        await interface.start()


@pytest.mark.asyncio
async def test_vlc_http_interface_start_process_handle_exists(create_vlc_http_interface):
    interface = create_vlc_http_interface()

    mock_process_handle = Mock()
    interface._process_handle = mock_process_handle

    with pytest.raises(ProcessStartupError):
        await interface.start()


@pytest.mark.asyncio
async def test_vlc_http_interface_stop_no_reader_handle(create_vlc_http_interface):
    logger = Mock()
    interface = create_vlc_http_interface(logger=logger)

    mock_reader_handle = AsyncMock()
    mock_reader_handle.cancel.side_effect = Exception("Oopsie!")
    interface._reader_handle = mock_reader_handle

    await interface.stop()

    logger.warning.assert_called_once()
    args, kwargs = logger.warning.call_args
    log_msg = args[0]
    assert "Failed to cancel reader task: " in log_msg


@pytest.mark.asyncio
async def test_vlc_http_interface_stop_no_process_handle(create_vlc_http_interface):
    logger = Mock()
    mock_async_process_manager = AsyncMock()
    interface = create_vlc_http_interface(
        async_process_manager=mock_async_process_manager,
        logger=logger
    )

    interface._process_handle = Mock()
    mock_async_process_manager.terminate.side_effect = Exception("Oopsie!")

    await interface.stop()

    logger.warning.assert_called_once()
    args, kwargs = logger.warning.call_args
    log_msg = args[0]
    assert "Failed to cancel process task: " in log_msg
