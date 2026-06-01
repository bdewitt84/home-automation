# tests/test_vlc_media_control.py

from unittest.mock import MagicMock, AsyncMock
import xml.etree.ElementTree as ET

import requests
from components.services.media.vlc_media_control import VlcMediaController


MOCK_VLC_GET_PATH = 'components.services.vlc_media_control.requests.get'
MOCK_VLC_HTTP_SERVER_URL = 'http://127.0.0.1:8080'
MOCK_VLC_PASSWORD = '<PASSWORD>'


def create_mock_response(return_status: dict) -> requests.Response:

    # build xml tree
    root = ET.Element("root")
    for key, value in return_status.items():
        element = ET.SubElement(root, key)
        element.text = value

    # build mock requests Response
    response = MagicMock()
    response.status_code = 200
    response.text = ET.tostring(root)

    return response


def create_mock_settings(server_url=None, password=None):

    mock_http_server_url = server_url or 'http://127.0.0.1:8080'
    mock_vlc_password = password or '<PASSWORD>'

    mock_settings = MagicMock()
    mock_settings.password = mock_vlc_password
    mock_settings.vlc_http_server_url = mock_http_server_url

    return mock_settings


def create_mock_client(state=None):

    return_status = {
        'state': state or 'Default'
    }
    mock_client = AsyncMock()
    mock_client.get.return_value = create_mock_response(return_status)
    return mock_client


def assert_request_made(mock_get: requests.Response | MagicMock, expected_params: dict) -> None:
    mock_get.assert_called_once()
    assert mock_get.call_args[1]['auth'] == ('', MOCK_VLC_PASSWORD)
    call_url = mock_get.call_args[0][0]
    expected_scheme = 'http://'
    expected_endpoint = '/requests/status.xml'
    assert expected_scheme in call_url
    assert expected_endpoint in call_url
    call_params = mock_get.call_args[1]['params']
    assert expected_params == call_params


async def test_play_success():

    # Arrange
    mock_client = create_mock_client('playing')
    mock_settings = create_mock_settings()
    vlc_media_control = VlcMediaController(mock_client, mock_settings)

    expected_params = {'command': 'pl_play'}

    # Act
    result = await vlc_media_control.play()

    # Assert
    mock_client.get.assert_called_once_with(MOCK_VLC_HTTP_SERVER_URL + '/requests/status.xml',
                                            auth=('', MOCK_VLC_PASSWORD),
                                            params=expected_params)
    assert result.state == 'playing'


async def test_stop_success():

    # Arrange
    mock_client = create_mock_client('stopped')
    mock_settings = create_mock_settings()
    vlc_media_control = VlcMediaController(mock_client, mock_settings)

    expected_params = {'command': 'pl_stop'}

    # Act
    result = await vlc_media_control.stop()

    # Assert
    mock_client.get.assert_called_once_with(MOCK_VLC_HTTP_SERVER_URL + '/requests/status.xml',
                                            auth=('', MOCK_VLC_PASSWORD),
                                            params=expected_params)
    assert result.state == 'stopped'


async def test_enqueue_success():

    # Arrange
    mock_client = create_mock_client()
    mock_settings = create_mock_settings()
    vlc_media_control = VlcMediaController(mock_client, mock_settings)

    mock_path = 'mock_path'
    expected_params = {'command': 'in_enqueue', 'input': mock_path}

    # Act
    result = await vlc_media_control.enqueue(mock_path)

    # Assert
    mock_client.get.assert_called_once_with(MOCK_VLC_HTTP_SERVER_URL + '/requests/status.xml',
                                            auth=('', MOCK_VLC_PASSWORD),
                                            params=expected_params)
