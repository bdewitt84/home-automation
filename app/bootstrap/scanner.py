# app/bootstrap/scanner.py

import importlib
import pkgutil
from typing import Type, Any, Callable, Iterator
from types import ModuleType

from interfaces import FactoryInterface

from config.project import FACTORY_PACKAGE_PATH

ModuleInfo = Any


def scan_for_components(path: str,
                        module_importer: Type[Callable[[str], ModuleType]] = importlib.import_module,
                        package_walker: Type[Callable[[str], Iterator[ModuleInfo]]] = pkgutil.walk_packages
                        ) -> None:
    """
    Imports all modules at package root 'path', forcing the registration
    decorators to populate the registry with application components and
    their associated metadata.
    :param path:
    :param module_importer:
    :param package_walker:
    :return:
    """
    package = module_importer(path)
    for _finder, name, _is_pkg in package_walker(package.__path__):
        module_name = package.__name__ + '.' + name
        module_importer(module_name)
        print(f"Imported component {module_name}")


def _get_factory_name_for_class(cls: type[Any]) -> str:
    return cls.__name__ + "Factory"


def _factory_loader(factory_name: str,
                    factory_package_path: str=FACTORY_PACKAGE_PATH,
                    importer: Callable[[str], ModuleType] = importlib.import_module,
                    ) -> Type[FactoryInterface]:
    factory_module = importer(factory_package_path)
    factory_cls = getattr(factory_module, factory_name)
    return factory_cls
