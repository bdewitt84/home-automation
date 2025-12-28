# tests/test_registry.py
from unittest.mock import Mock

import app.di.registry
from app.di.registry import register_component_with_container, ComponentMetadata, COMPONENT_METADATA_REGISTRY, clear_registry


def test_clear_registry():

    mock_service_cls = Mock()
    mock_metadata = ComponentMetadata(
        'mock_key',
        100,
        'mock_scope'
    )

    app.di.registry.COMPONENT_METADATA_REGISTRY = {mock_service_cls: mock_metadata}

    clear_registry()

    assert len(COMPONENT_METADATA_REGISTRY.items()) == 0


def test_register_component_with_container():

    test_key = 'test_key'
    test_lifecycle = 100

    @register_component_with_container(test_key, test_lifecycle)
    class TestComponent:
        pass

    assert TestComponent in COMPONENT_METADATA_REGISTRY
    metadata: ComponentMetadata = COMPONENT_METADATA_REGISTRY[TestComponent]
    assert metadata.key == test_key
    assert metadata.lifecycle == test_lifecycle

    clear_registry()
