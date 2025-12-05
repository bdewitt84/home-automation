# config/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class VLCMediaControllerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='VLC_MEDIA_CONTROLLER_',
        case_sensitive=False,
        env_file='.env',
        env_file_encoding='utf-8',
    )

    URL: str = Field(
        'http://127.0.0.1:8080',
        description='VLC HTTP interface URL'
    )

    PASSWORD: str = Field(
        'your_password',
        description='VLC HTTP interface password'
    )


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='APP_',
        case_sensitive=False,
        env_file='.env',
        env_file_encoding='utf-8',
    )

    media: VLCMediaControllerSettings = VLCMediaControllerSettings()


settings = AppSettings()
