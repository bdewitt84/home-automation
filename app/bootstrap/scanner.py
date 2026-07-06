# app/bootstrap/scanner.py

import importlib
import pkgutil
from pkgutil import ModuleInfo
from typing import Type, Callable, Iterator, Iterable
from types import ModuleType


def scan_for_components(path: str,
                        module_importer: Type[Callable[[str], ModuleType]] = importlib.import_module,
                        package_walker: Type[Callable[[Iterable[str]], Iterator[ModuleInfo]]] = pkgutil.walk_packages
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
        print(f"Scanner: Imported '{module_name}'")


class Scanner:
    def __init__(self,
                 package_walker: Callable[[Iterable[str]], Iterator[ModuleInfo]]=pkgutil.walk_packages,
                 module_importer: Callable[[str], ModuleType]=importlib.import_module, ):
        self._package_walker = package_walker
        self._package_importer = module_importer
        self._scanned_modules: list[str] = []

    def scan_packages(self, path: list[str]) -> list[str]:
        found = []
        for item in path:
            package = self._package_importer(item)
            found.extend([
                package.__name__ + '.' + name
                for _finder, name, _is_pkg
                in self._package_walker(package.__path__)
            ])
        self._scanned_modules.extend(found)
        return found

    def get_scanned_modules(self) -> list[str]:
        return self._scanned_modules

    def import_scanned_modules(self):
        for module in self._scanned_modules:
            self._package_importer(module)
        self.clear()

    def clear(self):
        self._scanned_modules.clear()
