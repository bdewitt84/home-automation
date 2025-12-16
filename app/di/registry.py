# app/di/registry.py

from typing import Dict, Type, Any
from interfaces.factory_interface import FactoryInterface


COMPONENT_METADATA_REGISTRY: Dict[Type[Any], Dict[str, Any]] = {}


def register_component_with_container(key:str, lifecycle: int=0):

    def decorator(cls):
        COMPONENT_METADATA_REGISTRY[cls] = {
            'key': key,
            'lifecycle': lifecycle,
        }
        return cls

    return decorator
