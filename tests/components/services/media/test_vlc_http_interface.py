# ./tests/components/services/media/test_vlc_http_interface.py

import pytest
from unittest.mock import AsyncMock, Mock

from app.exceptions.system import ProcessStartupError
from components.services.media.vlc_http_interface import (
    VlcHttpInterface,
    VlcHttpInterfaceSettings,
)


@pytest.fixture
def fake_settings():
    settings = VlcHttpInterfaceSettings()
    return settings


@pytest.fixture
def mock_async_process_manager():
    manager = AsyncMock()
    return manager


@pytest.fixture
def mock_async_reader_factory():
    reader = AsyncMock()
    return reader


@pytest.mark.asyncio
async def test_vlc_http_interface_start(fake_settings,
                                  mock_async_process_manager,
                                  mock_async_reader_factory
                                  ):
    interface = VlcHttpInterface(settings=fake_settings,
                                 async_process_manager=mock_async_process_manager,
                                 async_reader_factory=mock_async_reader_factory
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
async def test_vlc_http_interface_stop(fake_settings, mock_async_process_manager, mock_async_reader_factory):
    interface = VlcHttpInterface(settings=fake_settings,
                                 async_process_manager=mock_async_process_manager,
                                 async_reader_factory=mock_async_reader_factory
                                 )

    mock_reader_handle = AsyncMock()
    interface._reader_handle = mock_reader_handle

    mock_process_handle = AsyncMock()
    id = 42
    mock_process_handle.id = id
    interface._process_handle = mock_process_handle

    await interface.stop()

    mock_reader_handle.cancel.assert_awaited_once()
    mock_async_process_manager.terminate.assert_awaited_once_with(pid=id)


@pytest.mark.asyncio
async def test_vlc_http_interface_start_reader_handle_exists(
        fake_settings, mock_async_process_manager, mock_async_reader_factory):
    interface = VlcHttpInterface(settings=fake_settings,
                                 async_process_manager=mock_async_process_manager,
                                 async_reader_factory=mock_async_reader_factory)

    mock_reader_handle = Mock()
    interface._reader_handle = mock_reader_handle

    with pytest.raises(ProcessStartupError):
        await interface.start()


@pytest.mark.asyncio
async def test_vlc_http_interface_start_process_handle_exists(
        fake_settings, mock_async_process_manager, mock_async_reader_factory):
    interface = VlcHttpInterface(settings=fake_settings,
                                 async_process_manager=mock_async_process_manager,
                                 async_reader_factory=mock_async_reader_factory)

    mock_process_handle = Mock()
    interface._process_handle = mock_process_handle

    with pytest.raises(ProcessStartupError):
        await interface.start()


@pytest.mark.asyncio
async def test_vlc_http_interface_stop_no_reader_handle(
        fake_settings, mock_async_process_manager, mock_async_reader_factory):
    # todo: test logging once implemented
    raise NotImplemented


@pytest.mark.asyncio
async def test_vlc_http_interface_stop_no_process_handle(
        fake_settings, mock_async_process_manager, mock_async_reader_factory):
    # todo: test logging once implemented
    raise NotImplemented
