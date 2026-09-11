from _typeshed import Incomplete
from dataclasses import dataclass
from pathlib import Path
from sage.libs.gap.element import GapElement
__all__ = ['GapPackage', 'FUNCTOR_CATEGORIES', 'SLICE_CATEGORIES', 'FINITE_SETS_PACKAGES', 'FINITE_CATEGORY_PACKAGES', 'PRESENTED_MODULE_PACKAGES', 'package_directory', 'load_repository_package', 'load_packages']

@dataclass(frozen=True, slots=True)
class GapPackage:
    name: str
    version: str
FUNCTOR_CATEGORIES: Incomplete
SLICE_CATEGORIES: Incomplete
FINITE_SETS_PACKAGES: Incomplete
FINITE_CATEGORY_PACKAGES: Incomplete
PRESENTED_MODULE_PACKAGES: Incomplete

def package_directory(package: GapPackage) -> Path:
    ...

def load_repository_package(package: GapPackage) -> GapElement:
    ...

def load_packages(packages: tuple[GapPackage, ...]) -> tuple[GapElement, ...]:
    ...
