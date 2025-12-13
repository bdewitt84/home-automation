# app/di/factories/vlc_process_manager_factory.py

from app.di.container import DependencyContainer
from app.di.keys import APP_SETTINGS_KEY
from config.settings import AppSettings
from interfaces.factory_interface import FactoryInterface
from services.media import VLCProcessManager


class VlcProcessManagerFactory(FactoryInterface):
    def __init__(self, container: DependencyContainer):
        super().__init__(container)


    def create(self):
        settings: AppSettings = self._container.resolve(APP_SETTINGS_KEY)

        url: str = settings.url
        port: int = settings.port
        password: str = settings.password

        return VLCProcessManager(url, port, password)
