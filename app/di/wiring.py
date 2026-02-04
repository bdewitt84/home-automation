# app/wiring.py

"""
    Handles getting singletons from factories and attaching them to the
    application's dependency container
"""

from app.di.container import DependencyContainer

from app.di.keys import (
    APP_SETTINGS_KEY,
)


from config.settings import settings, AppSettings


def register_settings(container: DependencyContainer) -> None:
    """
    Registers an instance of Pydantic BaseSettings containing application
    configuration settings. The settings are already initialized and are
    imported from config.settings.settings
    :param container: dependency container
    :returns: None
    """
    container.register_factory(
        APP_SETTINGS_KEY,
        lambda: settings,
    )
    container.map_type_to_key(AppSettings, APP_SETTINGS_KEY)
