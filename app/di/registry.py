# app/di/registry.py

from typing import Dict, Type, Any
from dataclasses import dataclass


SERVICE_CLS_INDEX = 0
METADATA_INDEX = 1


class Scopes:
    SINGLETON = "SINGLETON"
    TRANSIENT = "TRANSIENT"
    # REQUEST = "REQUEST"


@dataclass
class ComponentMetadata:
    key: str
    lifecycle: int
    scope: str = Scopes.SINGLETON


COMPONENT_METADATA_REGISTRY: Dict[Type[Any], ComponentMetadata] = {}


def register_component_with_container(key:str, lifecycle: int=0):

    def decorator(cls):
        COMPONENT_METADATA_REGISTRY[cls] = ComponentMetadata(
            key=key,
            lifecycle=lifecycle,
            scope=Scopes.SINGLETON,
        )
        print(f"Registered {cls.__name__} with key {key}")
        return cls

    return decorator


def clear_registry():
    COMPONENT_METADATA_REGISTRY.clear()
