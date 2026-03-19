# app/bootstrap/wiring.py
import inspect
from typing import Type, Any, Callable

from fastapi import FastAPI

from app.di.container import DependencyContainer
from app.di.registry import ComponentMetadata
from app.di.decorators import ControllerInfo, RouteInfo
from app.lifecycle_manager import LifeCycleManager
from config.supported_platforms import SUPPORTED_PLATFORMS
from interfaces import SystemService


class MultipleControllerBaseError(Exception): pass


def filter_signature_params(sig: inspect.Signature,
                            names: list[str]):
    filtered_params =[
        p
        for name, p in sig.parameters.items()
        if name not in names
    ]
    return sig.replace(parameters=filtered_params)


def _create_handler(cls: type,
                    abc: type,
                    method_name: str,
                    container: DependencyContainer,
                    sig_inspector: Callable[[object], Any] = inspect.signature,
                    ) -> Callable:

    target_method = getattr(abc, method_name)
    orig_signature = sig_inspector(target_method)
    filtered_signature = filter_signature_params(orig_signature, ['self'])

    async def handler(**kwargs):
        service = container.resolve_by_type(cls)
        func = getattr(service, method_name)
        if inspect.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            return func(**kwargs)

    handler.__signature__ = filtered_signature
    handler.__name__ = method_name

    return handler


def build_full_path(prefix: str,
                    path: str
                    ) -> str:
    clean_prefix = prefix.strip('/')
    clean_path = path.lstrip('/')
    return f'/{clean_prefix}/{clean_path}'


def get_controller_base(cls):
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


def wire_controller_methods(cls: type,
                            base_cls: type,
                            ctrl_info: ControllerInfo,
                            app: FastAPI,
                            container: DependencyContainer,):

    base_methods = inspect.getmembers(base_cls, predicate=inspect.isfunction)
    for name, method in base_methods:
        if not hasattr(method, '_route_info'):
            continue

        route_info: RouteInfo = method._route_info
        full_path = build_full_path(ctrl_info.prefix, route_info.path)
        handler = _create_handler(cls, base_cls, name, container)

        app.add_api_route(path=full_path,
                          endpoint=handler,
                          methods=route_info.methods,
                          tags=ctrl_info.tags,)

        print(f"Wiring: added route {full_path}")


def build_api_routes(app: FastAPI,
                     container: DependencyContainer,
                     registry: dict[type, ComponentMetadata]
                     ):

    for cls, metadata in registry.items():
        if not hasattr(cls, '_controller_info'):
            continue

        print(f"Wiring: found controller {cls.__name__}")
        base_cls = get_controller_base(cls)
        ctrl_info = base_cls._controller_info
        wire_controller_methods(cls, base_cls, ctrl_info, app, container)


def wire_system_service(container: DependencyContainer,
                        platform: str
                        ) -> None:
    service_cls = SUPPORTED_PLATFORMS.get(platform)
    if service_cls is None:
        raise RuntimeError(f"Platform {platform} is not supported")

    metadata: ComponentMetadata = ComponentMetadata(
        key=SystemService.__name__,
        type=SystemService,
        is_dependency=True,
    )

    container.register_component(metadata.key, service_cls, metadata)


def wire_infrastructure_components(registry: dict[Type[Any], ComponentMetadata],
                                   container: DependencyContainer,
                                   ) -> None:

    for _component_cls, metadata in registry.items():
        if metadata.is_dependency:
            try:
                container.register_component(metadata.key, _component_cls, metadata, overrides=None)

            except Exception as e:
                raise RuntimeError(f"Critical wiring failure for {_component_cls.__name__}: {e}") from e


def get_metadata_by_key(key: str,
    registry: dict[Type[Any], ComponentMetadata],
    )-> ComponentMetadata | None:

    for metadata in registry.values():
        if metadata.key == key:
            return metadata


def wire_user_components(config_data: dict,
                         container: DependencyContainer,
                         registry: dict[Type[Any], ComponentMetadata],
                         ) -> None:

    components_config = config_data.get('components', {})

    for component_name, component_data in components_config.items():

        type_name = component_data['type']
        metadata = get_metadata_by_key(type_name, registry)
        if not metadata:
            print(f"Warning: No metadata found for component type '{type_name}'")
            continue

        settings_cls = metadata.settings_cls
        settings_data = component_data.get('settings', {})
        settings_instance = settings_cls(**settings_data)
        overrides = {'settings': settings_instance}

        container.register_component(
            key=component_name,
            cls=metadata.type,
            metadata=metadata,
            overrides=overrides,
        )


def wire_lifecycle_management(container: DependencyContainer,
                              manager: LifeCycleManager
                              ) -> None:
    for key in container.get_lifecycle_keys():
        instance = container.resolve(key)
        manager.index_singleton(instance)
