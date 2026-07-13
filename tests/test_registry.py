# tests/test_registry.py

import pytest

import app.di.registry
from app.di.registry import component, METADATA_REGISTRY, clear_registry
from app.models.component import ComponentMetadata


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

    app.di.registry.METADATA_REGISTRY.update({MockComponent: mock_metadata})

    clear_registry()

    assert len(METADATA_REGISTRY.items()) == 0


def test_register_component_with_container():

    test_key = 'test_key'
    test_lifecycle = 100

    @component(
        key=test_key,
        lifecycle=test_lifecycle)
    class TestComponent:
        def __init__(self, int_param: int, str_param: str):
            pass

    assert TestComponent in METADATA_REGISTRY
    metadata: ComponentMetadata = METADATA_REGISTRY[TestComponent]
    assert metadata.key == test_key
    assert metadata.lifecycle == test_lifecycle
    assert metadata.requirements["int_param"] == int
    assert metadata.requirements["str_param"] == str
    assert "self" not in metadata.requirements

    clear_registry()
