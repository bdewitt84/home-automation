# ./app/di/introspector.py

from typing import Type, Any, Callable
from inspect import signature
from app.exceptions.inspection import AnnotationNotFoundError


class Introspector:
    def __init__(self):
        pass

    def get_requirements(self,
                         target: Type[Any] | Callable,
                         ) -> dict[str, Type]:

        sig = signature(target)
        requirements = {}

        for name, param in sig.parameters.items():
            arg_type = param.annotation

            if arg_type is param.empty:
                raise AnnotationNotFoundError(f"Parameter {name} has no annotation")

            if arg_type is None:
                raise ValueError(f"Parameter {name} must not have annotation 'None'")

            requirements[name] = arg_type

        return requirements
