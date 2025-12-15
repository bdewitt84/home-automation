# app/di/registry.py

from typing import Dict, Type, Any
from interfaces.factory_interface import FactoryInterface


SERVICE_REGISTRY: Dict[Type[Any], Dict[str, Any]] = {}


def register_service(key:str, lifecycle: bool=False):

    def decorator(cls):
        SERVICE_REGISTRY[cls] = {
            'key': key,
            'lifecycle': lifecycle,
        }
        return cls

    return decorator
