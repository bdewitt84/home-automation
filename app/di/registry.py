# app/di/registry.py

from typing import Dict, Type, Any

from typing_extensions import TypedDict

COMPONENT_METADATA_REGISTRY: Dict[Type[Any], Dict[str, Any]] = {}


class Scopes:
    SINGLETON = "SINGLETON"
    TRANSIENT = "TRANSIENT"
    # REQUEST = "REQUEST"


class ComponentMetadata(TypedDict):
    key: str
    lifecycle: int


def register_component_with_container(key:str, lifecycle: int=0):

    def decorator(cls):
        COMPONENT_METADATA_REGISTRY[cls]: ComponentMetadata = {
            'key': key,
            'lifecycle': lifecycle,
        }
        print(f"Registered {cls.__name__} with key {key}")
        return cls

    return decorator
