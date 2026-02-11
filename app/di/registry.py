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
    is_dependency: bool = False
    lifecycle: int = 0


COMPONENT_METADATA_REGISTRY: Dict[Type[Any], ComponentMetadata] = {}


def component(key:str=None,
              settings_cls=None,
              is_dependency=False,
              lifecycle: int=0
              ) -> Any:

    def decorator(cls):

        effective_key = key if key else cls.__name__

        COMPONENT_METADATA_REGISTRY[cls] = ComponentMetadata(
            key=effective_key,
            type=cls,
            scope=Scopes.SINGLETON,
            settings_cls=settings_cls,
            is_dependency=is_dependency,
            lifecycle=lifecycle,
        )
        print(f"Registry: Registered {cls.__name__} with key {effective_key}")
        return cls

    return decorator


def clear_registry():
    COMPONENT_METADATA_REGISTRY.clear()
