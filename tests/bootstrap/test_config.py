# ./tests/bootstrap/test_config.py

import pytest
from unittest.mock import Mock, mock_open
from app.bootstrap.loader import Loader


@pytest.fixture
def reader():
    return mock_open()

@pytest.fixture
def decoder():
    decoder = Mock()
    decoder.return_value = {"key": "value"}
    return decoder

@pytest.fixture
def parser():
    parser = Mock()
    parser.return_value = "fake parsed data"
    return parser

@pytest.fixture
def interpolator():
    interpolator = Mock()
    return interpolator


def test_load_from_path(reader, decoder, parser, interpolator):

    fake_path = "fake_path"

    loader = Loader(reader=reader,
                    decoder=decoder,
                    parser=parser,
                    interpolator=interpolator)

    loaded_config = loader.load_from_path(fake_path)

    reader.assert_called_once_with(file=fake_path, mode='r')
    decoder.assert_called_once_with(reader.return_value)
    interpolator.assert_called_once_with(decoder.return_value)
    parser.assert_called_once_with(decoder.return_value)
    assert loaded_config == parser.return_value
