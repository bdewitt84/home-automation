# tests/test_builder.py
import pytest
from unittest.mock import Mock, ANY, MagicMock

import inspect
from abc import ABC, abstractmethod

from app.di.container import DependencyContainer
from app.models.component import Scopes, ComponentMetadata
from app.routing.builder import RouteBuilder
from app.routing.decorators import controller, route


@pytest.fixture
def registry():
    registry: dict[type, ComponentMetadata] = {}
    return registry


@pytest.fixture
def container():
    container = DependencyContainer()
    container.register_self()
    return container

@pytest.fixture
def mock_fastapi():
    app = Mock()
    return app


def populate_registry(registry, component):

    metadata = ComponentMetadata(
        key = component.__name__,
        type = component,
        scope = Scopes.SINGLETON,
        settings_cls = None,
        is_dependency = False,
        lifecycle = 0,
    )

    registry.update({component: metadata})


def test_build_api_routes(registry, container, mock_fastapi):

    # Arrange
    @controller(prefix="mock_controller",
                tags=["ctrl_tag"], )
    class MockController():
        def __init__(self):
            pass

        @route(path="mock_path",
               methods=["mock_method"],
               tags=["route_tag"])
        async def mock_handler(self):
            """
            mock_docs
            """
            pass

    populate_registry(registry, MockController)
    builder = RouteBuilder(mock_fastapi, container)

    # Act
    builder.build_api_routes(registry)

    # Assert
    mock_fastapi.add_api_route.assert_called_with(
        path='/mock_controller/mock_path',
        endpoint=ANY,
        methods=['mock_method'],
        tags=['ctrl_tag', 'route_tag'],
        summary='\n            mock_docs\n            '
    )


class SyncMockController:
    def mock_endpoint(self, param: int=666):
        return param


class AsyncMockController:
    async def mock_endpoint(self, param: int=666):
        return param


@pytest.mark.parametrize("mock_controller, expected_async",
                         [
                             (SyncMockController, False),
                             (AsyncMockController, True),
                         ])
async def test_create_handler(mock_controller, expected_async, registry, mock_fastapi, container):

    # Arrange
    builder = RouteBuilder(mock_fastapi, container)
    controller_instance = mock_controller()
    container.resolve_by_type = MagicMock(return_value=controller_instance)
    expected_result = 42

    # Act
    handler = builder._create_handler(mock_controller, 'mock_endpoint')

    if expected_async:
        handler_result = await handler(param=expected_result)
    else:
        handler_result = handler(param=expected_result)

    # Assert

    assert inspect.iscoroutinefunction(handler) is expected_async # Handler is async iff the endpoint is async
    assert handler_result == expected_result    # Handler returns the correct value
    container.resolve_by_type.assert_called_once_with(mock_controller)  # Container was asked for the right controller


def test_forge_signature(mock_fastapi, container):

    # Arrange
    builder = RouteBuilder(mock_fastapi, container)


    class MockInterface(ABC):
        @abstractmethod
        def mock_endpoint(self, param: int):
            pass

    class MockController(MockInterface):
        def mock_endpoint(self, param: int = 666):
            return param

    handler = lambda x: MockController().mock_endpoint(x)

    # def handler(**kwargs):
    #     return MockController().mock_endpoint(**kwargs)

    # Act
    print('\n', inspect.signature(handler).parameters)
    builder._forge_signature(MockInterface,
                             'mock_endpoint',
                             handler)

    # Assert
    params = inspect.signature(handler).parameters  # Get parameters from the handler
    assert 'self' not in params # Make sure 'self' gets filtered
    assert handler.__name__ == 'mock_endpoint'
    assert 'param' in params    # Make sure the other parameter is attached
