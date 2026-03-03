# tests/test_container.py

import pytest

from unittest.mock import Mock

from app.di.component_registry import DuplicateKeyError, FactoryNotFoundError, TypeNotFoundError
from app.di.container import DependencyContainer, DependencyNotFoundError
from app.di.registry import ComponentMetadata, component


class MockDependency: pass

@pytest.fixture
def container():
    return DependencyContainer()

@pytest.fixture
def metadata():
    return ComponentMetadata(
        key='test',
        type=MockDependency,
        is_dependency=False,
    )

def generate_metadata(cls, is_dependency=False):
    return ComponentMetadata(
        key=cls.__name__,
        type=cls,
        is_dependency=is_dependency,
    )

def create_bulk_component_data(n:int, start:int=0):
    key_factory_metadata = []
    for i in range(start, n + start):
        key = 'test_' + str(i)
        metadata = ComponentMetadata(key=key, type=MockDependency)
        metadata.key = key
        key_factory_metadata.append((key, lambda: None, metadata))

    return key_factory_metadata



def test_register_factory_success(container):
    key = 'test'
    instance = Mock()
    factory = lambda: instance
    metadata = Mock()
    container.register_factory(key, factory, metadata)

    result = container.resolve(key)

    assert result == instance


def test_register_factory_duplicate_key(container):
    container.register_factory('test', lambda: None, Mock())

    with pytest.raises(DuplicateKeyError):
        container.register_factory('test', lambda: None, Mock())


def test_register_factory_already_registered(container, metadata):
    metadata.is_dependency = True

    container.register_factory(metadata.key, lambda: None, metadata)

    with pytest.raises(DuplicateKeyError):
        container.register_factory('different_key', lambda: None, metadata)


def test_resolve_success_flat(container, metadata):
    factory = lambda: None
    container.register_factory('test', factory, metadata)

    result = container.resolve('test')

    assert result == factory()


def test_resolve_success_recursive(container):
    class DependencyA: pass
    metadata_a = generate_metadata(DependencyA, True)
    class DependencyB: pass
    metadata_b = generate_metadata(DependencyB, True)
    class MockComponent:
        def __init__(self, dep_a:DependencyA, dep_b:DependencyB):
            self.dep_a = dep_a
            self.dep_b = dep_b
    metadata_comp = generate_metadata(MockComponent)

    container.register_component(metadata_a.key, metadata_a.type, metadata_a)
    container.register_component(metadata_b.key, metadata_b.type, metadata_b)
    container.register_component(metadata_comp.key, metadata_comp.type, metadata_comp)

    result: MockComponent = container.resolve(metadata_comp.key)

    assert isinstance(result, MockComponent)
    assert isinstance(result.dep_a, DependencyA)
    assert isinstance(result.dep_b, DependencyB)


def test_resolve_not_registered(container):

    with pytest.raises(FactoryNotFoundError):
        container.resolve('unregistered key')


def test_resolve_by_type_success(container, metadata):
    metadata.is_dependency = True
    instance = Mock()
    factory = lambda: instance
    container.register_factory(metadata.key, factory, metadata)

    result = container.resolve_by_type(MockDependency)

    assert result == instance


def test_resolve_by_type_not_registered(container):
    with pytest.raises(TypeNotFoundError):
        container.resolve_by_type(MockDependency)


def test_get_metadata(container, metadata):
    container.register_factory('test', lambda: None, metadata)

    result = container.get_metadata('test')

    assert result == metadata


def test_get_all_metadata(container):

    key_factory_metadata = create_bulk_component_data(9)
    for k, f, m in key_factory_metadata:
        container.register_factory(k, f, m)

    result = container.get_all_registered_metadata()

    for key, _, metadata in key_factory_metadata:
        assert result[key] == metadata


def test_get_registered_component_keys(container):

    key_factory_metadata = create_bulk_component_data(9)
    for k, f, m in key_factory_metadata:
        container.register_factory(k, f, m)

    result = container.get_registered_component_keys()

    for key, _, _ in key_factory_metadata:
        assert key in result


def test_get_lifecycle_keys(container):

    component_data = [
        {"key": "late", "lifecycle": 10},
        {"key": "early", "lifecycle": 1},
        {"key": "none", "lifecycle": 0},
        {"key": "middle", "lifecycle": 5},
    ]

    for item in component_data:
        key = item["key"]
        lifecycle = item["lifecycle"]
        metadata = ComponentMetadata(key, MockDependency, lifecycle=lifecycle)
        container.register_factory(key, lambda: None, metadata)

    result = container.get_lifecycle_keys()

    assert result == ["early", "middle", "late"]


def test_get_resolved_dependencies(container):
    class DependencyA: pass
    class DependencyB: pass
    requirements = {
        "parameter_a": DependencyA,
        "parameter_b": DependencyB,
    }
    container.register_factory("DependencyA", lambda: DependencyA(), ComponentMetadata(
        key="DependencyA",
        type=DependencyA,
        is_dependency=True,
    ))
    container.register_factory("DependencyB", lambda: DependencyB(), ComponentMetadata(
        key="DependencyB",
        type=DependencyB,
        is_dependency=True,
    ))

    result = container._get_resolved_dependencies(requirements)

    assert isinstance(result["parameter_a"], DependencyA)
    assert isinstance(result["parameter_b"], DependencyB)


def test_validate_pass_no_overrides(container):
    class DependencyA: pass
    class DependencyB: pass

    requirements = {
        "DependencyA": DependencyA,
        "DependencyB": DependencyB,
    }

    container.register_factory("DependencyA", lambda: DependencyA(), ComponentMetadata(
        key="DependencyA",
        type=DependencyA,
        is_dependency=True,
    ))
    container.register_factory("DependencyB", lambda: DependencyB(), ComponentMetadata(
        key="DependencyB",
        type=DependencyB,
        is_dependency=True,
    ))

    container._validate(requirements, {})
    pass # does not throw


def test_validate_pass_with_override(container):
    class DependencyA: pass
    class DependencyB: pass
    requirements = {
        "registered": DependencyA,
        "not_registered": DependencyB,
    }
    overrides = {
        "not_registered": DependencyB(),
    }
    container.register_factory("DependencyA", lambda: DependencyA(), ComponentMetadata(
        key="DependencyA",
        type=DependencyA,
        is_dependency=True,
    ))

    container._validate(requirements, overrides)
    pass  # does not throw


def test_validate_fail_not_registered_not_in_overrides(container):
    class DependencyA: pass

    class DependencyB: pass

    requirements = {
        "registered": DependencyA,
        "not_registered": DependencyB,
    }
    container.register_factory("DependencyA", lambda: DependencyA(), ComponentMetadata(
        key="DependencyA",
        type=DependencyA,
        is_dependency=True,
    ))

    with pytest.raises(DependencyNotFoundError) as e:
        container._validate(requirements, {})
    assert 'registered' in str(e.value)
    assert 'override' in str(e.value)


def test_create_factory(container):

    class MockComponent: pass

    factory = container._create_factory(MockComponent, {}, {})
    result = factory()

    assert isinstance(result, MockComponent)


def test_register_component(container):
    class MockComponent: pass
    container.register_component(
        "MockComponent",
        MockComponent,
        ComponentMetadata(
            key="MockComponent",
            type=MockComponent,
        ),
        {}
    )

    result = container.resolve("MockComponent")

    assert isinstance(result, MockComponent)


def test_register_self(container):
    container.register_self()

    result = container.resolve(container.__class__.__name__)

    assert isinstance(result, DependencyContainer)
