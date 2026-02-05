# config/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='APP_',
        case_sensitive=False,
        env_file='.env',
        env_file_encoding='utf-8',
    )

settings = AppSettings()
