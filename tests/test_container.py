# tests/test_container.py
from typing import Type, Any

import pytest

from unittest.mock import Mock

from app.exceptions.di import DuplicateKeyError, FactoryNotFoundError, TypeNotFoundError, CycleDetectedError, \
    DependencyNotFoundError
from app.di.container import DependencyContainer, MetadataNotFoundError
from app.models.component import ComponentMetadata


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

def generate_metadata(cls: Type, requirements: dict[str, Type[Any]]=None , is_dependency=False):
    return ComponentMetadata(
        key=cls.__name__,
        type=cls,
        requirements=requirements or {},
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

    class DependencyC: pass

    class DependencyB:
        def __init__(self, dep_c: DependencyC):
            self.dep_c = dep_c

    class DependencyA:
        def __init__(self, dep_b:DependencyB):
            self.dep_b = dep_b

    requirements_b = {"dep_c": DependencyC}
    requirements_a = {"dep_b": DependencyB}

    metadata_c = generate_metadata(DependencyC, {}, is_dependency=True)
    metadata_b = generate_metadata(DependencyB, requirements_b, is_dependency=True)
    metadata_a = generate_metadata(DependencyA, requirements_a, is_dependency=True)

    container.register_component(metadata_c.key, metadata_c.type, metadata_c)
    container.register_component(metadata_b.key, metadata_b.type, metadata_b)
    container.register_component(metadata_a.key, metadata_a.type, metadata_a)

    result: DependencyA = container.resolve(metadata_a.key)

    assert isinstance(result, DependencyA)
    assert isinstance(result.dep_b, DependencyB)
    assert isinstance(result.dep_b.dep_c, DependencyC)


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
        generate_metadata(MockComponent),
        {}
    )

    result = container.resolve("MockComponent")

    assert isinstance(result, MockComponent)

def test_register_component_invalid_metadata(container):
    class MockComponent: pass

    with pytest.raises(ValueError) as e:
        container.register_component(
            key='MockComponent',
            cls=MockComponent,
            metadata='invalid_metadata', # type: ignore
        )

def test_register_self(container):
    container.register_self()

    result = container.resolve(container.__class__.__name__)

    assert isinstance(result, DependencyContainer)


def test_validate_graph_dfs_no_cycle(container):
    """
            D
          /
        B
      /   \
    A       E
      \   /
        C

    :param container:
    :return:
    """
    container.register_self()

    class DependencyE: pass
    class DependencyD: pass
    class DependencyC:
        def __init__(self, dep_e: DependencyE):
            self.dep_e = dep_e
    class DependencyB:
        def __init__(self, dep_d: DependencyD, dep_e: DependencyE):
            self.dep_d = dep_d
            self.dep_e = dep_e
    class DependencyA:
        def __init__(self, dep_b: DependencyB, dep_c: DependencyC):
            self.dep_b = dep_b
            self.dep_c = dep_c

    req_b: dict[str, Type] = {"dep_d": DependencyD, "dep_e": DependencyE,}
    req_c: dict[str, Type] = {"dep_e": DependencyE,}
    req_a: dict[str, Type] = {"dep_b": DependencyB, "dep_c": DependencyC,}

    data: list[tuple[Type, dict[str,Type]]] = [
        (DependencyE, None),
        (DependencyD, None),
        (DependencyC, req_c),
        (DependencyB, req_b),
        (DependencyA, req_a),
    ]

    for cls, req in data:
        meta = generate_metadata(cls=cls, requirements=req, is_dependency=True,)
        container.register_component(key=cls.__name__, cls=cls, metadata=meta)

    container.validate_graph_dfs()
    pass # did not raise


def test_validate_graph_dfs_with_cycle(container):
    container.register_self()
    class DependencyC: pass
    class DependencyB: pass
    class DependencyA: pass

    req_c: dict[str, Type] = {"dep_a": DependencyA,}
    req_b: dict[str, Type] = {"dep_c": DependencyC,}
    req_a: dict[str, Type] = {"dep_b": DependencyB,}

    data: [tuple[Type, dict[str,Type]]] = [
        (DependencyC, req_c),
        (DependencyB, req_b),
        (DependencyA, req_a),
    ]

    for cls, req in data:
        meta = generate_metadata(cls=cls, requirements=req, is_dependency=True,)
        container.register_component(key=cls.__name__, cls=cls, metadata=meta)

    with pytest.raises(CycleDetectedError) as e:
        container.validate_graph_dfs()


def test_validate_graph_dfs_dependency_not_found(container):
    container.register_self()

    class DependencyB: pass
    class DependencyA: pass

    req_b: dict[str, Type] = {"dep_a": DependencyA,}
    req_a: dict[str, Type] = {}

    meta_b = generate_metadata(cls=DependencyB, requirements=req_b, is_dependency=True)
    meta_a = None

    container.register_component(key=DependencyB.__name__, cls=DependencyB, metadata=meta_b,)

    with pytest.raises(DependencyNotFoundError) as e:
        container.validate_graph_dfs()
