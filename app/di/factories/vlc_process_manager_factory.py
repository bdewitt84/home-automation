# app/di/factories/vlc_process_manager_factory.py

from app.di.container import DependencyContainer
from app.di.keys import APP_SETTINGS_KEY
from config.settings import AppSettings
from interfaces.factory_interface import FactoryInterface
from services.media import VlcProcessManager


class VlcProcessManagerFactory(FactoryInterface):
    def __init__(self, container: DependencyContainer):
        super().__init__(container)


    def create(self):
        settings: AppSettings = self._container.resolve(APP_SETTINGS_KEY)

        host: str = settings.vlc.HOST
        port: str = settings.vlc.PORT
        password: str = settings.vlc.PASSWORD

        return VlcProcessManager(host, port, password)
