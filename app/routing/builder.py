# app/routing/builder.py
from fastapi import FastAPI
from typing import Any, Callable

from app.routing.decorators import ControllerInfo, RouteInfo
from app.di.container import DependencyContainer
from app.di.registry import ComponentMetadata

from inspect import Signature, signature, getmembers, isfunction, iscoroutinefunction
class MultipleControllerBaseError(Exception): pass


class RouteBuilder:
    def __init__(self,
                 app: FastAPI,
                 container: DependencyContainer,
                 ):
        self.app = app
        self.container = container

    def _filter_signature_params(self,
                                 sig: Signature,
                                 names: list[str]):
        filtered_params =[
            p
            for name, p in sig.parameters.items()
            if name not in names
        ]
        return sig.replace(parameters=filtered_params)


    def _create_handler(self,
                        cls: type,
                        method_name: str,
                        ) -> Callable:

        # handler for async methods
        async def async_handler(**kwargs):
            service = self.container.resolve_by_type(cls)
            func = getattr(service, method_name)
            return await func(**kwargs)

        # handler for sync methods
        def sync_handler(**kwargs):
            service = self.container.resolve_by_type(cls)
            func = getattr(service, method_name)
            return func(**kwargs)

        # determine which handler to use
        func = getattr(cls, method_name)
        if iscoroutinefunction(func):
            handler = async_handler
        else:
            handler = sync_handler

        return handler

    def _forge_signature(self,
                         abc: type,
                         method_name: str,
                         handler: Callable[..., Any],
                         sig_inspector: Callable[[object], Any] = signature,
                         ) -> None:
        target_method = getattr(abc, method_name)
        orig_signature = sig_inspector(target_method)
        filtered_signature = self._filter_signature_params(orig_signature, ['self'])
        handler.__signature__ = filtered_signature
        handler.__name__ = method_name

    def _build_full_path(self,
                         prefix: str,
                         path: str
                         ) -> str:
        clean_prefix = prefix.strip('/')
        clean_path = path.lstrip('/')
        return f'/{clean_prefix}/{clean_path}'


    def _get_controller_base(self,
                             cls):
        controller_base = None
        for base in cls.__mro__:
            if not hasattr(base, '_controller_info'):
                continue
            if base is cls:
                continue
            if controller_base is not None and base != controller_base:
                raise MultipleControllerBaseError(f"Multiple controller bases found for {cls.__name__}, {controller_base.__name__} and {base.__name__}")

            controller_base = base

        return controller_base or cls


    def _wire_controller_methods(self,
                                 cls: type,
                                 base_cls: type,
                                 ctrl_info: ControllerInfo
                                 ):

        base_methods = getmembers(base_cls, predicate=isfunction)
        for name, method in base_methods:
            if not hasattr(method, '_route_info'):
                continue

            route_info: RouteInfo = method._route_info
            full_path = self._build_full_path(ctrl_info.prefix, route_info.path)
            handler = self._create_handler(cls, name)
            self._forge_signature(base_cls, name, handler)
            tags = ctrl_info.tags + route_info.tags
            summary = method.__doc__ or name.replace("_", " ").capitalize()

            self.app.add_api_route(path=full_path,
                              endpoint=handler,
                              methods=route_info.methods,
                              tags=tags,
                              summary=summary)

            print(f"Wiring: added route {full_path}")


    def build_api_routes(self,
                         registry: dict[type, ComponentMetadata]
                         ):

        for cls, metadata in registry.items():
            if not hasattr(cls, '_controller_info'):
                continue

            print(f"Wiring: found controller {cls.__name__}")
            base_cls = self._get_controller_base(cls)
            ctrl_info = base_cls._controller_info
            self._wire_controller_methods(cls, base_cls, ctrl_info)
