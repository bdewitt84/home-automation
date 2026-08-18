# tests/test_introspector.py

import pytest

from app.di.introspector import Introspector, AnnotationNotFoundError
from app.models.component import DependencyRequirement


@pytest.fixture
def introspector():
    return Introspector()


def test_get_requirements_success(introspector):

    class MockClass:
        def __init__(self, param_str:str, param_int: int=42):
            pass

    result = introspector.get_requirements(MockClass)

    expected = {
        "param_str": DependencyRequirement(
            type=str,
            has_default=False,
        ),
        "param_int": DependencyRequirement(
            type=int,
            has_default=True,
        )
    }

    assert result == expected


def test_get_requirements_no_annotation(introspector):
    class MockClass:
        def __init__(self, param_without_annotation):
            pass

    with pytest.raises(AnnotationNotFoundError):
        introspector.get_requirements(MockClass)


def test_get_requirements_annotation_is_none(introspector):
    class MockClass:
        def __init__(self, param: None):
            pass

    with pytest.raises(ValueError):
        introspector.get_requirements(MockClass)
