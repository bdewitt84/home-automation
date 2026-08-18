# tests/test_container.py

import pytest
from unittest.mock import Mock
from typing import Type

from app.di.container import DependencyContainer
from app.models.component import ComponentMetadata, DependencyRequirement
from app.exceptions.di import (
    DuplicateKeyError,
    FactoryNotFoundError,
    TypeNotFoundError,
    DependencyNotFoundError,
)


class MockDependency: pass


@pytest.fixture
def container():
    return DependencyContainer()


@pytest.fixture
def metadata_is_not_dependency():
    return ComponentMetadata(
        key='test',
        type=MockDependency,
        is_dependency=False,
    )

@pytest.fixture
def metadata_is_dependency():
    return ComponentMetadata(
        key='test',
        type=MockDependency,
        is_dependency=True,
    )

def generate_metadata(cls: Type, requirements: dict[str, DependencyRequirement] = None, is_dependency=True):
    return ComponentMetadata(
        key=cls.__name__,
        type=cls,
        requirements=requirements or {},
        is_dependency=is_dependency,
    )


def create_bulk_component_data(n: int, start: int = 0):
    key_factory_metadata = []
    for i in range(start, n + start):
        key = f'test_{i}'
        metadata = ComponentMetadata(key=key, type=MockDependency)
        key_factory_metadata.append((key, lambda: None, metadata))
    return key_factory_metadata


def test_register_factory_success(container):
    instance = Mock()
    container.register_factory(
        key='test',
        factory=lambda: instance,
        overrides={},
        metadata=Mock()
    )
    assert container.resolve('test') == instance


def test_register_factory_with_default(container):

    class DefaultDependency: pass

    default_dep_instance = DefaultDependency()

    class FakeComponent:
        def __init__(self, default_dep: DefaultDependency=default_dep_instance):
            self.default_dep = default_dep

    metadata = generate_metadata(
        cls=FakeComponent,
        requirements={
            "default_dep": DependencyRequirement(
                type=DefaultDependency,
                has_default=True,
            )
        }
    )

    container.register_component(
        key="test",
        cls=FakeComponent,
        metadata=metadata,
        overrides={},
    )

    result: FakeComponent = container.resolve("test")

    assert result.default_dep is default_dep_instance


def test_register_factory_duplicate_key(container):
    container.register_factory(key='test', factory=lambda: None, overrides={}, metadata=Mock())
    with pytest.raises(DuplicateKeyError):
        container.register_factory(key='test', factory=lambda: None, overrides={}, metadata=Mock())


def test_register_factory_already_registered(container, metadata_is_dependency):
    container.register_factory(key=metadata_is_dependency.key, factory=lambda: None, overrides={}, metadata=metadata_is_dependency)
    with pytest.raises(DuplicateKeyError):
        container.register_factory(key='different_key', factory=lambda: None, overrides={}, metadata=metadata_is_dependency)


def test_resolve_success_flat(container, metadata_is_not_dependency):
    factory = lambda: None
    container.register_factory(key='test', factory=factory, overrides={}, metadata=metadata_is_not_dependency)
    assert container.resolve('test') == factory()


def test_resolve_success_recursive(container):
    class DependencyC: pass

    class DependencyB:
        def __init__(self, dep_c: DependencyC):
            self.dep_c = dep_c

    class DependencyA:
        def __init__(self, dep_b: DependencyB):
            self.dep_b = dep_b

    metadata_c = generate_metadata(DependencyC)
    metadata_b = generate_metadata(
        cls=DependencyB,
        requirements={"dep_c": DependencyRequirement(type=DependencyC)}
    )
    metadata_a = generate_metadata(
        cls=DependencyA,
        requirements={"dep_b": DependencyRequirement(type=DependencyB)}
    )

    for meta in [metadata_c, metadata_b, metadata_a]:
        container.register_component(key=meta.key, cls=meta.type, metadata=meta, overrides={})

    result: DependencyA = container.resolve(metadata_a.key)

    assert isinstance(result, DependencyA)
    assert isinstance(result.dep_b, DependencyB)
    assert isinstance(result.dep_b.dep_c, DependencyC)


def test_resolve_not_registered(container):
    with pytest.raises(FactoryNotFoundError):
        container.resolve('unregistered key')


def test_resolve_by_type_success(container, metadata_is_dependency):
    instance = Mock()
    container.register_factory(key=metadata_is_dependency.key, factory=lambda: instance, overrides={}, metadata=metadata_is_dependency)
    assert container.resolve_by_type(MockDependency) == instance


def test_resolve_by_type_not_registered(container):
    with pytest.raises(TypeNotFoundError):
        container.resolve_by_type(MockDependency)


def test_get_metadata(container, metadata_is_not_dependency):
    container.register_factory(key='test', factory=lambda: None, overrides={}, metadata=metadata_is_not_dependency)
    assert container.get_metadata('test') == metadata_is_not_dependency


def test_get_all_metadata(container):
    key_factory_metadata = create_bulk_component_data(9)
    for k, f, m in key_factory_metadata:
        container.register_factory(key=k, factory=f, overrides={}, metadata=m)

    result = container.get_all_registered_metadata()
    for key, _, metadata in key_factory_metadata:
        assert result[key] == metadata


def test_get_registered_component_keys(container):
    key_factory_metadata = create_bulk_component_data(9)
    for k, f, m in key_factory_metadata:
        container.register_factory(key=k, factory=f, overrides={}, metadata=m)

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
        metadata = ComponentMetadata(key, MockDependency, lifecycle=item["lifecycle"])
        container.register_factory(key=key, factory=lambda: None, overrides={}, metadata=metadata)

    assert container.get_lifecycle_keys() == ["early", "middle", "late"]


def test_get_resolved_dependencies(container):
    class DependencyA: pass

    class DependencyB: pass

    container.register_factory(
        key="DependencyA",
        factory=lambda: DependencyA(),
        overrides={},
        metadata=generate_metadata(DependencyA)
    )
    container.register_factory(
        key="DependencyB",
        factory=lambda: DependencyB(),
        overrides={},
        metadata=generate_metadata(DependencyB)
    )

    result = container._get_resolved_dependencies({
        "parameter_a": DependencyRequirement(DependencyA),
        "parameter_b": DependencyRequirement(DependencyB),
    })

    assert isinstance(result["parameter_a"], DependencyA)
    assert isinstance(result["parameter_b"], DependencyB)


def test_validate_pass_no_overrides(container):
    class DependencyA: pass

    class DependencyB: pass

    for cls in [DependencyA, DependencyB]:
        container.register_factory(
            key=cls.__name__,
            factory=lambda: cls(),
            overrides={},
            metadata=generate_metadata(cls)
        )

    container._validate({"DependencyA": DependencyA, "DependencyB": DependencyB}, {})


def test_validate_pass_with_override(container):
    class DependencyA: pass

    class DependencyB: pass

    container.register_factory(
        key="DependencyA",
        factory=lambda: DependencyA(),
        overrides={},
        metadata=generate_metadata(DependencyA)
    )

    requirements = {"registered": DependencyA, "not_registered": DependencyB}
    overrides = {"not_registered": DependencyB()}

    container._validate(requirements, overrides)


def test_validate_fail_not_registered_not_in_overrides(container):
    class DependencyA: pass

    class DependencyB: pass

    container.register_factory(
        key="DependencyA",
        factory=lambda: DependencyA(),
        overrides={},
        metadata=generate_metadata(DependencyA)
    )

    with pytest.raises(DependencyNotFoundError) as e:
        container._validate({"registered": DependencyA, "not_registered": DependencyB}, {})

    assert 'registered' in str(e.value)
    assert 'override' in str(e.value)


def test_create_factory(container):
    class MockComponent: pass

    factory = container._create_factory(MockComponent, {}, {})
    assert isinstance(factory(), MockComponent)


def test_register_component(container):
    class MockComponent: pass

    container.register_component(
        key="MockComponent",
        cls=MockComponent,
        metadata=generate_metadata(MockComponent),
        overrides={}
    )
    assert isinstance(container.resolve("MockComponent"), MockComponent)


def test_register_component_invalid_metadata(container):
    class MockComponent: pass

    with pytest.raises(ValueError):
        container.register_component(
            key='MockComponent',
            cls=MockComponent,
            metadata='invalid_metadata',  # type: ignore
            overrides={}
        )


def test_register_self(container):
    container.register_self()
    assert isinstance(container.resolve(container.__class__.__name__), DependencyContainer)
