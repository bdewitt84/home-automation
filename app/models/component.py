#./app/models/component.py

from dataclasses import dataclass
from typing import Type, Any

from pydantic import BaseModel


class Scopes:
    SINGLETON = "SINGLETON"
    TRANSIENT = "TRANSIENT"
    # REQUEST = "REQUEST"


@dataclass
class ComponentMetadata:
    key: str
    type: Type[Any]
    scope: str = Scopes.SINGLETON
    requirements: dict[str, Type[Any]] | None = None
    settings_cls: Type[BaseModel] | None = None
    is_dependency: bool = False
    lifecycle: int = 0
