# api/providers.py

from app.di.container import DependencyContainer
from fastapi import Request, HTTPException
from app.di.keys import (
    CONTAINER_KEY, MEDIA_CONTROL_SERVICE_KEY,
)


def _get_dependency(key: str, container: DependencyContainer) -> any:
    try:
        dependency = container.resolve(key)
        return dependency
    except KeyError:
        raise HTTPException(
            status_code=500,
            detail=f"Application misconfiguration: {key} not registered.",
        )


def get_media_control_service(request: Request):
    container = getattr(request.app.state, CONTAINER_KEY)
    return _get_dependency(MEDIA_CONTROL_SERVICE_KEY, container)