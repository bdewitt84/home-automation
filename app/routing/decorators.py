# app/routing/decorators.py

from dataclasses import dataclass, field
from typing import List, Callable, Any


@dataclass
class ControllerInfo:
    prefix: str
    tags: [str] = field(default_factory=list)


@dataclass
class RouteInfo:
    path: str
    methods: List[str] = field(default_factory=lambda: ["GET"])
    tags: List[str] = field(default_factory=list)


def controller(prefix: str = None,
               tags: list[str] = None):
    def decorator(cls: type):
        cls._controller_info = ControllerInfo(
            prefix=prefix.lstrip("/") or cls.__name__,
            tags=tags or [cls.__name__],
        )
        print(f"Routing: controller info attached to class {cls.__name__} ")
        return cls

    return decorator


def route(path: str, methods: List[str] = None, tags: List[str] = None):
    def decorator(func: Callable):
        # Attach a custom attribute to the function object
        func._route_info = RouteInfo(
            path=path,
            methods=methods or ["GET"],
            tags=tags or []
        )
        print(f"Routing: route info attached to method {func.__name__} ")
        return func
    return decorator
