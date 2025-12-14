# services/media/vlc_media_control.py

from interfaces.media_control_interface import MediaControlInterface, MediaControlStatus
from xml.etree import ElementTree as ET
import requests


class VLCMediaControl(MediaControlInterface):

    def __init__(self, vlc_http_server_url: str, password: str=''):
        super().__init__()
        self.vlc_http_server_url = vlc_http_server_url
        self.auth = ('', password)

    def _construct_request_url(self) -> str:
        return self.vlc_http_server_url + '/requests/status.xml'

    def _send_command(self, params) -> requests.Response:
        request_url = self._construct_request_url()
        response = requests.get(request_url, auth=self.auth, params=params)
        response.raise_for_status()
        return response

    def _xml_to_dict(self, xml_tree: ET.Element, field_names: list[str]) -> dict:
        """
        Converts all first level XML elements with name in field_names into a Python dictionary.
        :param xml_tree: The root element of the XML tree
        :param field_names: List of names of XML elements to convert
        :returns: dict with first level XML elements as keys and values
        """
        return {
            field_name: xml_tree.find(field_name).text
            for field_name in field_names
            if xml_tree.find(field_name) is not None
        }

    def _coerce_digit_to_int(self, d: dict) -> dict:
        """
        Converts all digit values of a dictionary to integers.
        :param d:
        :return: new dictionary with all digits converted to integers
        """
        coerced = d.copy()
        for key, value in coerced.items():
            if value.isdigit():
                coerced.update({key: int(value)})
        return coerced

    def _parse_response(self, response) -> MediaControlStatus:

        try:
            # build xml tree
            xml_string = response.text
            xml_tree = ET.fromstring(xml_string)

            # get names of elements to convert to dict entries
            field_names = MediaControlStatus.model_fields.keys()

            # convert xml data to dict and coerce digits to ints
            data = self._xml_to_dict(xml_tree, field_names)
            coerced_data = self._coerce_digit_to_int(data)

            # build status object from dict
            status = MediaControlStatus(**coerced_data)

            return status

        except ET.ParseError as e:
            print(f"XML parser error: {e}")
            raise ValueError("Failed to parse XML response from VLC") from e

    def play(self) -> MediaControlStatus:
        params = { 'command': 'pl_play' }
        response = self._send_command(params)
        status = self._parse_response(response)
        return status

    def stop(self) -> MediaControlStatus:
        params = { 'command': 'pl_stop' }
        response = self._send_command(params)
        status = self._parse_response(response)
        return status

    def enqueue(self, filepath: str) -> MediaControlStatus:
        params = {
            'command': 'in_enqueue',
            'input': filepath,
        }
        response = self._send_command(params)
        status = self._parse_response(response)
        return status
