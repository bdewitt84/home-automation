# app/dependencies/factories/vlc_media_control_factory.py

from interfaces.factory_interface import FactoryInterface
from app.container import DependencyContainer
from config.settings import AppSettings
from app.dependencies.container_keys import APP_SETTINGS_KEY
from services.media.vlc_media_control import VLCMediaControl


class VlcMediaControlFactory(FactoryInterface):
    def __init__(self, container: DependencyContainer):
        super().__init__(container)

    def create(self):
        settings: AppSettings = self._container.resolve(APP_SETTINGS_KEY)
        url = settings.media.URL
        password = settings.media.PASSWORD
        return VLCMediaControl(url, password)
