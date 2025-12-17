# app/di/registry.py

from typing import Dict, Type, Any


COMPONENT_METADATA_REGISTRY: Dict[Type[Any], Dict[str, Any]] = {}


class Scopes:
    SINGLETON = "SINGLETON"
    TRANSIENT = "TRANSIENT"
    # REQUEST = "REQUEST"


def register_component_with_container(key:str, lifecycle: int=0):

    def decorator(cls):
        COMPONENT_METADATA_REGISTRY[cls] = {
            'key': key,
            'lifecycle': lifecycle,
        }
        print(f"Registered {cls.__name__} with key {key}")
        return cls

    return decorator
