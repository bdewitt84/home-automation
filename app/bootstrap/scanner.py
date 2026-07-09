# app/bootstrap/scanner.py

import importlib
import pkgutil
from pkgutil import ModuleInfo
from typing import Callable, Iterator, Iterable
from types import ModuleType


class Scanner:
    def __init__(self,
                 package_walker: Callable[[Iterable[str], str], Iterator[ModuleInfo]]=pkgutil.walk_packages,
                 module_importer: Callable[[str], ModuleType]=importlib.import_module, ):
        self._package_walker = package_walker
        self._module_importer = module_importer
        self._scanned_modules: list[str] = []

    def scan_packages(self, path: list[str]) -> list[str]:
        """
        Scans all modules at package root 'path'
        """
        found = []
        for item in path:
            package = self._module_importer(item)
            prefix = package.__name__ + '.'
            found.extend([
                name
                for _finder, name, _is_pkg
                in self._package_walker(package.__path__, prefix)
            ])
        self._add_modules(found)
        return found

    def get_scanned_modules(self) -> list[str]:
        return self._scanned_modules

    def import_scanned_modules(self):
        """
        Imports all modules found using _scan_packages, forcing the registration
        decorators to populate the registry with application components and
        their associated metadata.
        :return:
        """
        for module in self._scanned_modules:
            self._module_importer(module)
            print(f"Scanner: Imported '{module}'")
        self.clear()

    def _add_modules(self, modules: list[str]):
        self._scanned_modules.extend(modules)

    def clear(self):
        self._scanned_modules.clear()
