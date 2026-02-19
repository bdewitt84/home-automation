# config/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.di.keys import APP_SETTINGS_KEY
from app.di.registry import component


@component(key=APP_SETTINGS_KEY,
           is_dependency=True
           )
class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='APP_',
        case_sensitive=False,
        env_file='.env',
        env_file_encoding='utf-8',
    )
