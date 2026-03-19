# app/routing/builder.py
from fastapi import FastAPI
from typing import Any, Callable

from app.routing.decorators import ControllerInfo, RouteInfo
from app.di.container import DependencyContainer
from app.di.registry import ComponentMetadata

from inspect import Signature, Parameter, signature, getmembers, isfunction, iscoroutinefunction
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
                        abc: type,
                        method_name: str,
                        sig_inspector: Callable[[object], Any] = signature,
                        ) -> Callable:

        target_method = getattr(abc, method_name)
        orig_signature = sig_inspector(target_method)
        filtered_signature = self._filter_signature_params(orig_signature, ['self'])

        async def handler(**kwargs):
            service = self.container.resolve_by_type(cls)
            func = getattr(service, method_name)
            if iscoroutinefunction(func):
                return await func(**kwargs)
            else:
                return func(**kwargs)

        handler.__signature__ = filtered_signature
        handler.__name__ = method_name

        return handler


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
            handler = self._create_handler(cls, base_cls, name)

            self.app.add_api_route(path=full_path,
                              endpoint=handler,
                              methods=route_info.methods,
                              tags=ctrl_info.tags,)

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
