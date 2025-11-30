# tests/test_vlc_media_control.py

from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET

import requests

from services.media.vlc_media_control import VLCMediaControl
from interfaces.media_control_interface import MediaControlStatus


MOCK_VLC_GET_PATH = 'services.vlc_media_control.requests.get'
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

def test_play_success():

    # Arrange
    return_status = {
        'state': 'playing'
    }
    response = create_mock_response(return_status)
    vlc_media_control = VLCMediaControl(MOCK_VLC_HTTP_SERVER_URL, MOCK_VLC_PASSWORD)
    expected_params = {'command': 'pl_play'}

    # Act
    with patch('requests.get', return_value=response) as mock_get:
        result = vlc_media_control.play()

    # Assert
    assert_request_made(mock_get, expected_params)
    assert result.state == 'playing'

def test_stop_success():
    return_status = { 'state': 'stopped' }
    response = create_mock_response(return_status)
    vlc_media_control = VLCMediaControl(MOCK_VLC_HTTP_SERVER_URL, MOCK_VLC_PASSWORD)
    expected_params = { 'command': 'pl_stop' }

    # Act
    with patch('requests.get', return_value=response) as mock_get:
        result = vlc_media_control.stop()

    # Assert
    assert_request_made(mock_get, expected_params)
    assert result.state == 'stopped'

def test_enqueue_success():

    return_status = {}
    response = create_mock_response(return_status)
    mock_path = 'video.mp4'
    expected_params = {
        'command': 'in_enqueue',
        'input': mock_path
    }
    vlc_media_control = VLCMediaControl(MOCK_VLC_HTTP_SERVER_URL, MOCK_VLC_PASSWORD)

    with patch('requests.get', return_value=response) as mock_get:
        result = vlc_media_control.enqueue(mock_path)

    assert_request_made(mock_get, expected_params)
    assert isinstance(result, MediaControlStatus)
