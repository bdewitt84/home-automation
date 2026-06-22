# ./components/infrastructure/providers.py

from components.infrastructure.os_utils import OSUtils
from config import supported_platforms
from app.di.registry import component
from components.services.debian_system_service import DebianSystemService
from interfaces import SystemService


@component(key='SystemService',
           is_dependency=True)
def system_service_provider(os_utils: OSUtils) -> SystemService:
    return DebianSystemService(os_utils)
