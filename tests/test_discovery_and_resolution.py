# tests/test_discovery_and_resolution.py

import pytest
import sys
import textwrap
import importlib


from app.bootstrap.scanner import scan_for_components
from app.bootstrap.wiring import wire_infrastructure_components
from app.di.container import DependencyContainer
from app.di.registry import COMPONENT_METADATA_REGISTRY


@pytest.fixture
def container():
    return DependencyContainer()


def test_discovery_and_resolution(container, tmp_path):

    comp_dir = tmp_path / "components"
    comp_dir.mkdir()
    (comp_dir / "__init__.py").write_text("")

    comp_file = comp_dir / "test_component.py"
    comp_file.write_text(textwrap.dedent("""
        from app.di.registry import component
        
        
        @component(is_dependency=True)
        class TestComponent:
            def __init__(self):
                self.data = 'test_data'
    """))

    sys.path.insert(0, str(tmp_path))
    importlib.invalidate_caches()

    try:
        scan_for_components('components')
        wire_infrastructure_components(registry=COMPONENT_METADATA_REGISTRY,
                                       container=container)

        result = container.resolve('TestComponent')
        assert result.data == 'test_data'

    finally:
        sys.path.pop(0)
        COMPONENT_METADATA_REGISTRY.clear()
