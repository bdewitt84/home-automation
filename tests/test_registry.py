# tests/test_registry.py

import pytest

import app.di.registry
from app.di.registry import component, ComponentMetadata, COMPONENT_METADATA_REGISTRY, clear_registry


@pytest.fixture(autouse=True)
def cleanup():
    yield
    clear_registry()


def test_clear_registry():
    class MockComponent: pass

    mock_metadata = ComponentMetadata(
        key='mock_key',
        type=MockComponent,
    )

    app.di.registry.COMPONENT_METADATA_REGISTRY.update({MockComponent: mock_metadata})

    clear_registry()

    assert len(COMPONENT_METADATA_REGISTRY.items()) == 0


def test_register_component_with_container():

    test_key = 'test_key'
    test_lifecycle = 100

    @component(
        key=test_key,
        lifecycle=test_lifecycle)
    class TestComponent:
        pass

    assert TestComponent in COMPONENT_METADATA_REGISTRY
    metadata: ComponentMetadata = COMPONENT_METADATA_REGISTRY[TestComponent]
    assert metadata.key == test_key
    assert metadata.lifecycle == test_lifecycle

    clear_registry()
