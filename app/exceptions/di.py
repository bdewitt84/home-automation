# ./apps/exceptions/di.py


class DuplicateKeyError(Exception):
    pass


class FactoryNotFoundError(Exception):
    pass


class TypeNotFoundError(Exception):
    pass


class MetadataNotFoundError(Exception):
    pass


class GraphValidationError(Exception):
    pass


class CycleDetectedError(GraphValidationError):
    pass


class DependencyNotFoundError(GraphValidationError):
    pass


class RequirementsNotFoundError(GraphValidationError):
    pass


class IllegalDependencyError(GraphValidationError):
    pass
