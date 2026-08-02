# ./tests/bootstrap/parser.py
from unittest.mock import Mock

import pytest
from pydantic import BaseModel
import copy

from app.bootstrap.parser import ConfigParser
from app.exceptions.di import MetadataNotFoundError
from app.models.component import ComponentMetadata
from app.models.config import Config


@pytest.fixture
def registry():
    class FakeComponent: pass
    fake_component_metadata = ComponentMetadata(
        key='fake_component',
        type=FakeComponent,
        settings_cls=None,
    )
    return {
        FakeComponent: fake_component_metadata
    }


@pytest.fixture
def config():
    return {
        'version': '1.0.0',
        'app_settings': {},
        'components': {
            'fake_component': {
                'name': 'fake_component',
                'type': 'FakeComponent',
                'settings': {
                    'setting_1': 'value_1',
                }
            }
        }
    }


@pytest.fixture
def parser(registry):
    return ConfigParser(registry=registry)


def test_parser(config):
    # Arrange
    class FakeComponent: pass

    class FakeSettings(BaseModel):
        setting_1: str

    fake_component_metadata = ComponentMetadata(
        key=FakeComponent.__name__,
        type=FakeComponent,
        settings_cls=FakeSettings,
        )

    registry = {
        FakeComponent: fake_component_metadata
    }

    parser = ConfigParser(registry=registry)

    # Act
    result: Config = parser.parse_config(config)

    # Assert
    assert "fake_component" in result.components, "Component not found in the parsed config."
    parsed_component = result.components['fake_component']
    assert parsed_component.name == 'fake_component', "Component name is not correct."
    assert parsed_component.type == FakeComponent.__name__, "Component type is not correct."
    assert isinstance(parsed_component.settings, FakeSettings), "Component settings are not of the correct type."
    assert parsed_component.settings.setting_1 == 'value_1', "Component settings are not correct."


def test_parser_invalid_settings(config):
    # Arrange
    class FakeComponent: pass

    class FakeSettings(BaseModel):
        setting_1: str

    fake_component_metadata = ComponentMetadata(
        key=FakeComponent.__name__,
        type=FakeComponent,
        settings_cls=FakeSettings,
        )

    registry = {
        FakeComponent: fake_component_metadata
    }

    config = copy.deepcopy(config)
    config["components"]["fake_component"]["settings"] = {"invalid" : "settings"}

    parser = ConfigParser(registry=registry)

    # Act
    with pytest.raises(ValueError) as e:
        parser.parse_config(config)

    assert "invalid settings" in str(e.value).lower()


def test_parser_metadata_not_found(config):
    # Arrange
    registry = {}

    parser = ConfigParser(registry=registry) # Type: ignore

    # Act
    with pytest.raises(MetadataNotFoundError):
        parser.parse_config(config)
