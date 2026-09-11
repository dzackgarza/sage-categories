from dataclasses import dataclass
from pathlib import Path

from _typeshed import Incomplete
from sage.libs.gap.element import GapElement

__all__ = [
    "FINITE_CATEGORY_PACKAGES",
    "FINITE_SETS_PACKAGES",
    "FUNCTOR_CATEGORIES",
    "PRESENTED_MODULE_PACKAGES",
    "SLICE_CATEGORIES",
    "GapPackage",
    "load_packages",
    "load_repository_package",
    "package_directory",
]

@dataclass(frozen=True, slots=True)
class GapPackage:
    name: str
    version: str

FUNCTOR_CATEGORIES: Incomplete
SLICE_CATEGORIES: Incomplete
FINITE_SETS_PACKAGES: Incomplete
FINITE_CATEGORY_PACKAGES: Incomplete
PRESENTED_MODULE_PACKAGES: Incomplete

def package_directory(package: GapPackage) -> Path: ...
def load_repository_package(package: GapPackage) -> GapElement: ...
def load_packages(packages: tuple[GapPackage, ...]) -> tuple[GapElement, ...]: ...
