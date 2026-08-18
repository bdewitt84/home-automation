# ./tests/di/test_builder.py
from unittest.mock import Mock

import pytest
from typing import Type, Any

from pydantic import BaseModel

from app.di.builder import ContainerBuilder
from app.models.component import ComponentMetadata, ComponentRegistration, DependencyRequirement
from app.exceptions.di import (
    GraphValidationError,
    CycleDetectedError,
    DependencyNotFoundError,
)
from app.models.config import Config, ConfigComponent


def generate_metadata(cls: Type, requirements: dict[str, Type[Any]] = None, is_dependency=True):
    return ComponentMetadata(
        key=cls.__name__,
        type=cls,
        requirements=requirements or {},
        is_dependency=is_dependency,
    )


def test_wire_infrastructure():
    # We need a builder with a mock container
    mock_container = Mock()

    # We need a metadata registry with infrastructure components ready
    class MockDependency: pass
    class MockNotDependency: pass

    mock_metadata_dependency = ComponentMetadata(
        key=MockDependency.__name__,
        type=MockDependency,
        is_dependency=True,
    )

    mock_metadata_not_dependency = ComponentMetadata(
        key=MockNotDependency.__name__,
        type=MockNotDependency,
        is_dependency=False,
    )

    mock_registry = {
        MockDependency: mock_metadata_dependency,
        MockNotDependency: mock_metadata_not_dependency,
    }

    builder = ContainerBuilder(container=mock_container,
                               registry=mock_registry,
                               config={})

    builder._wire_infrastructure()

    """
    Components with the `is_depoendency` flag set to True get wired
    as infrastructure. When this flag is set to false, they are not
    considered infrastructure, so we only expect one call to
    `register_component`
    """
    mock_container.register_component.assert_called_once_with(
       key=mock_metadata_dependency.key,
       cls=MockDependency,
       metadata=mock_metadata_dependency,
       overrides=None
    )


def test_wire_infrastructure_raises():
    class MockDependency: pass
    mock_metadata = ComponentMetadata(
        key=MockDependency.__name__,
        type='bad_data', # type: ignore
        is_dependency=True,
    )
    mock_registry = {
        MockDependency: mock_metadata,
    }

    mock_container = Mock()
    mock_container.register_component.side_effect = Exception()

    builder = ContainerBuilder(
        container=mock_container,
        registry=mock_registry,
        config={},
    )

    with pytest.raises(RuntimeError):
        builder._wire_infrastructure()


def test_wire_user_components():

    class MockDependency: pass
    mock_dependency_metadata = ComponentMetadata(
        key=MockDependency.__name__,
        type=MockDependency,
        is_dependency=True,
    )

    class MockSettings(BaseModel): pass
    mock_settings_instance = MockSettings()

    class MockUserComponent: pass
    mock_user_component_metadata = ComponentMetadata(
        key=MockUserComponent.__name__,
        type=MockUserComponent,
        settings_cls=MockSettings,
        is_dependency=False,
    )

    mock_container = Mock()
    mock_registry = {
        MockUserComponent: mock_user_component_metadata,
        MockDependency: mock_dependency_metadata,
    }

    mock_user_component_key = "mock_user_component_key"

    mock_user_config = Config(
        version="0.0.0",
        app_settings={},
        components={
            mock_user_component_key: ConfigComponent(
                type=MockUserComponent.__name__,
                name="mock_user_component",
                settings=mock_settings_instance,
            )
        }
    )

    builder = ContainerBuilder(
        container=mock_container,
        registry=mock_registry,
        config=mock_user_config,
    )

    builder._wire_user_components()

    mock_container.register_component.assert_called_once_with(
        key=mock_user_component_key,
        cls=mock_user_component_metadata.type,
        metadata=mock_user_component_metadata,
        overrides={"settings": mock_settings_instance},
    )


def test_wire_user_components_no_settings():
    """
    Test the behavior of the wire_user_components method when a component with no settings class is provided.
    """

    class MockDependency: pass

    mock_dependency_metadata = ComponentMetadata(
        key=MockDependency.__name__,
        type=MockDependency,
        is_dependency=True,
    )

    mock_settings_instance = Mock()
    mock_settings_cls = Mock()
    mock_settings_cls.return_value = mock_settings_instance

    class MockUserComponent: pass

    mock_user_component_metadata = ComponentMetadata(
        key=MockUserComponent.__name__,
        type=MockUserComponent,
        settings_cls=None, # type: ignore
        is_dependency=False,
    )

    mock_container = Mock()
    mock_registry = {
        MockUserComponent: mock_user_component_metadata,
        MockDependency: mock_dependency_metadata,
    }

    mock_user_component_key = "mock_user_component_key"
    mock_user_component_settings = None

    mock_user_config = Config(
        version="0.0.0",
        app_settings={},
        components={
            mock_user_component_key: ConfigComponent(
                type=MockUserComponent.__name__,
                name="mock_user_component",
                settings=mock_user_component_settings,
            )
        }
    )

    builder = ContainerBuilder(
        container=mock_container,
        registry=mock_registry,
        config=mock_user_config,
    )

    builder._wire_user_components()

    mock_container.register_component.assert_called_once_with(
        key=mock_user_component_key,
        cls=mock_user_component_metadata.type,
        metadata=mock_user_component_metadata,
        overrides={},
    )


def test_validate_graph_no_cycle():
    """
             D
           /
         B
       /   \
     A       E
       \   /
         C
    """
    container = Mock()
    builder = ContainerBuilder(container=container, registry={}, config={})
    builder._component_graph = {
        "DependencyE": {
            "requires": {},
            "is_dependency": True,
        },
        "DependencyD": {
            "requires": {},
            "is_dependency": True,
        },
        "DependencyC": {
            "requires": {"DependencyE": "DependencyE"},
            "is_dependency": True,
        },
        "DependencyB": {
            "requires": {"DependencyD": "DependencyD",
                         "DependencyE": "DependencyE"},
            "is_dependency": True,
        },
        "DependencyA": {
            "requires": {"DependencyB": "DependencyB",
                         "DependencyC": "DependencyC"},
            "is_dependency": False,
        }
    }

    builder._validate_dependency_graph()


def test_validate_graph_with_cycle():
    container = Mock()
    builder = ContainerBuilder(container=container, registry={}, config={})
    builder._component_graph = {
        "DependencyC": {
            "requires": {"DependencyB": "DependencyB"},
            "is_dependency": True,
        },
        "DependencyB": {
            "requires": {"DependencyA": "DependencyA"},
            "is_dependency": True,
        },
        "DependencyA": {
            "requires": {"DependencyC": "DependencyC"},
            "is_dependency": True,
        }
    }

    with pytest.raises(CycleDetectedError):
        builder._validate_dependency_graph()


def test_validate_graph_depends_on_non_dependency():
    container = Mock()
    builder = ContainerBuilder(container=container, registry={}, config={})
    builder._component_graph = {
        "DependencyB": {
            "requires": {"DependencyA": "DependencyA"},
            "is_dependency": True,
        },
        "DependencyA": {
            "requires": {},
            "is_dependency": False,
        }
    }

    with pytest.raises(GraphValidationError) as e:
        builder._validate_dependency_graph()


def test_build_component_graph():
    class FakeDependency: pass

    class FakeNonDependency: pass

    class FakeContainer():
        def __init__(self):
            self._records = {
                FakeDependency.__name__ : ComponentRegistration(
                    metadata=ComponentMetadata(
                        key=FakeDependency.__name__,
                        type=FakeDependency,
                        requirements={},
                        is_dependency=True,
                    ),
                    factory=lambda: FakeDependency(),
                    overrides={}
                ),
                FakeNonDependency.__name__ : ComponentRegistration(
                    metadata=ComponentMetadata(
                        key=FakeNonDependency.__name__,
                        type=FakeNonDependency,
                        requirements={
                            "FakeDependency": DependencyRequirement(
                                type=FakeDependency,
                                has_default=False
                            )
                        },
                        is_dependency=False,
                    ),
                    factory=lambda: FakeNonDependency(),
                    overrides={}
                )
            }
            self._type_to_key = {
                FakeDependency: FakeDependency.__name__,
                FakeNonDependency: FakeNonDependency.__name__,
            }

        def get_all_records(self):
            return self._records

        def get_key_by_type(self, cls):
            return self._type_to_key[cls]

    builder = ContainerBuilder(
        container=FakeContainer(), # type: ignore
        registry={},
        config={}
    )

    builder._build_dependency_graph()

    assert builder._component_graph == {
        FakeDependency.__name__: {
            "requires": {},
            "is_dependency": True,
        },
        FakeNonDependency.__name__: {
            "requires": {"FakeDependency": "FakeDependency"},
            "is_dependency": False,
        }
    }


def test_build_component_graph_dependency_not_found():

    """
    When a component is registered with `is_dependency=False`, it will not
    have a mapping from its type to its key in the container. This means that
    if it is required by another component, it will not be found in the
    mapping, and the builder must raise an error.
    """

    class FakeDependency: pass

    class FakeNonDependency: pass

    class FakeContainer:
        def __init__(self):
            self._records = {
                FakeDependency.__name__: ComponentRegistration(
                    metadata=ComponentMetadata(
                        key=FakeDependency.__name__,
                        type=FakeDependency,
                        requirements={
                            "FakeNonDependency": DependencyRequirement(
                                type=FakeNonDependency,
                                has_default=False
                            )
                        },
                        is_dependency=True,
                    ),
                    factory=lambda: FakeDependency(),
                    overrides={},
                ),
                FakeNonDependency.__name__: ComponentRegistration(
                    metadata=ComponentMetadata(
                        key=FakeNonDependency.__name__,
                        type=FakeNonDependency,
                        requirements={},
                        is_dependency=False,
                    ),
                    factory=lambda: FakeNonDependency(),
                )
            }
            self._type_to_key = {
                FakeDependency: FakeDependency.__name__,
            }

        def get_all_records(self):
            return self._records

        def get_key_by_type(self, cls):
            return self._type_to_key.get(cls, None)

    builder = ContainerBuilder(
        container=FakeContainer(),  # type: ignore
        registry={},
        config={}
    )

    with pytest.raises(DependencyNotFoundError):
        builder._build_dependency_graph()
