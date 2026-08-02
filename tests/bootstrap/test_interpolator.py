# ./tests/bootstrap/test_interpolator.py

import pytest
from unittest.mock import Mock

from app.bootstrap.interpolator import interpolate_environment_variables


@pytest.fixture
def env_loader():
    env_loader = Mock()
    mock_environment = {
        "env_var": "interpolated_value",
        "deep_env_var": "interpolated_value"
    }
    env_loader.side_effect = mock_environment.get
    return env_loader


def test_interpolate(env_loader):

    cfg = {"ordinary_key": "ordinary_value",
           "env_key": "${env_var}",
           "nested_key": {
               "deep_env_key": "${deep_env_var}"
           }
        }

    interpolate_environment_variables(cfg, env_loader)

    assert cfg["ordinary_key"] == "ordinary_value"
    assert cfg["env_key"] == "interpolated_value"
    assert cfg["nested_key"]["deep_env_key"] == "interpolated_value"


def test_interpolate_missing_env_var(env_loader):
    cfg = {
        "env_key": "${missing_env_var}"
    }

    with pytest.raises(ValueError):
        interpolate_environment_variables(cfg, env_loader)
