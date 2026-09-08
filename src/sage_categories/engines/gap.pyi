from pathlib import Path

from sage.libs.gap.element import GapElement

class GapPackage:
    name: str
    version: str
    def __init__(self, name: str, version: str) -> None: ...

FINITE_SETS_PACKAGES: tuple[GapPackage, ...]
FINITE_CATEGORY_PACKAGES: tuple[GapPackage, ...]
PRESENTED_MODULE_PACKAGES: tuple[GapPackage, ...]
FUNCTOR_CATEGORIES: GapPackage
SLICE_CATEGORIES: GapPackage

def package_directory(package: GapPackage) -> Path: ...
def load_packages(packages: tuple[GapPackage, ...]) -> tuple[GapElement, ...]: ...
def load_repository_package(package: GapPackage) -> GapElement: ...
