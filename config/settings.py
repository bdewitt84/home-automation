# config/settings.py

from pydantic import BaseModel, ConfigDict

import os

class AppSettings(BaseModel):
    model_config = ConfigDict(
        frozen=True,
    )
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_FILE_PATH: str = './config/config.json'
    SERVICE_PACKAGE_NAME: str = 'components'
    CONTROLLER_PACKAGE_NAME: str = 'api.v1.controllers'


app_settings = AppSettings()
