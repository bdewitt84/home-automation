# app/di/registry.py

from typing import Dict, Type, Any, Callable
from inspect import isfunction, signature, Signature

from app.models.component import Scopes, ComponentMetadata
from app.di.introspector import Introspector


SERVICE_CLS_INDEX = 0
METADATA_INDEX = 1

COMPONENT_METADATA_REGISTRY: Dict[Type[Any] | Callable, ComponentMetadata] = {}


def component(key:str=None,
              settings_cls=None,
              is_dependency=False,
              lifecycle: int=0
              ) -> Any:

    def decorator(cls: Type[Any] | Callable):

        effective_key = key if key else cls.__name__

        if isfunction(cls):
            sig = signature(cls)
            if sig.return_annotation is Signature.empty:
                raise TypeError(f"Function {cls.__name__} must have return annotation to be registered as a component provider")
            effective_type = sig.return_annotation
        else:
            effective_type = cls

        requirements = Introspector().get_requirements(cls)

        COMPONENT_METADATA_REGISTRY[cls] = ComponentMetadata(
            key=effective_key,
            type=effective_type,
            scope=Scopes.SINGLETON,
            requirements=requirements,
            settings_cls=settings_cls,
            is_dependency=is_dependency,
            lifecycle=lifecycle,
        )
        print(f"Registry: Registered {cls.__name__} with key {effective_key}")
        return cls

    return decorator


def clear_registry():
    COMPONENT_METADATA_REGISTRY.clear()
