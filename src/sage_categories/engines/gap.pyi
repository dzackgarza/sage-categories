from _typeshed import Incomplete
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from sage.libs.gap.element import GapElement

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

@cache
def load_repository_package(package: GapPackage) -> GapElement:
    ...

@cache
def load_packages(packages: tuple[GapPackage, ...]) -> tuple[GapElement, ...]:
    ...
