# app/di/factories/vlc_media_control_factory.py

from interfaces.factory_interface import FactoryInterface
from app.di.container import DependencyContainer
from config.settings import AppSettings
from app.di.keys import APP_SETTINGS_KEY
from components.services.media.vlc_media_control import VLCMediaControl


class VlcMediaControlFactory(FactoryInterface):
    def __init__(self, container: DependencyContainer):
        super().__init__(container)

    def create(self):
        settings: AppSettings = self._container.resolve(APP_SETTINGS_KEY)
        url = settings.media.URL
        password = settings.media.PASSWORD
        return VLCMediaControl(url, password)
