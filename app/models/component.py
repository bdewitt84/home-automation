#./app/models/component.py

from dataclasses import dataclass, field
from typing import Type, Any, Callable

from pydantic import BaseModel


class Scopes:
    SINGLETON = "SINGLETON"
    TRANSIENT = "TRANSIENT"
    # REQUEST = "REQUEST"


@dataclass(frozen=True)
class DependencyRequirement:
    type: Type[Any]
    has_default: bool = False


@dataclass(frozen=True)
class ComponentMetadata:
    key: str
    type: Type[Any]
    scope: str = Scopes.SINGLETON
    requirements: dict[str, DependencyRequirement] = field(default_factory=dict)
    settings_cls: Type[BaseModel] | None = None
    is_dependency: bool = False
    lifecycle: int = 0


@dataclass(frozen=True)
class ComponentRegistration:
    metadata: ComponentMetadata
    factory: Callable
    overrides: dict[str, Any] | None = None
