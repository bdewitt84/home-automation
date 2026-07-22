# config/settings.py

from pydantic_settings import BaseSettings
import os


class AppSettings(BaseSettings):
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_FILE_PATH: str = './config/config.json'
    SERVICE_PACKAGE_NAME: str = 'components'
    CONTROLLER_PACKAGE_NAME: str = 'api.v1.controllers'
