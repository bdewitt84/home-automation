# app/di/registry.py

from typing import Dict, Type, Any
from dataclasses import dataclass

from pydantic import BaseModel

SERVICE_CLS_INDEX = 0
METADATA_INDEX = 1


class Scopes:
    SINGLETON = "SINGLETON"
    TRANSIENT = "TRANSIENT"
    # REQUEST = "REQUEST"


@dataclass
class ComponentMetadata:
    key: str
    type: Type[Any]
    scope: str = Scopes.SINGLETON
    settings_cls: Type[BaseModel] | None = None
    register_at_startup: bool = False
    lifecycle: int = 0


COMPONENT_METADATA_REGISTRY: Dict[Type[Any], ComponentMetadata] = {}


def register_component_with_container(key:str=None,
                                      settings_cls=None,
                                      register_at_startup=False,
                                      lifecycle: int=0):

    def decorator(cls):
        COMPONENT_METADATA_REGISTRY[cls] = ComponentMetadata(
            key=key or cls.__name__,
            type=cls,
            scope=Scopes.SINGLETON,
            settings_cls=settings_cls,
            register_at_startup=register_at_startup,
            lifecycle=lifecycle,
        )
        print(f"Registered {cls.__name__} with key {key}")
        return cls

    return decorator


def clear_registry():
    COMPONENT_METADATA_REGISTRY.clear()
