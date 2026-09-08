"""The GAP runtime boundary used by native CAP-backed computations.

The repository installer puts exact package releases in ``.gap/pkg``. A Sage
process has its own embedded GAP session, so this module forces that live session
to the repository-local installations before loading any package. GAP's
``SetPackagePath`` is the authority for selecting an installed release; every path
is fixed before the first ``LoadPackage`` call so dependencies cannot be satisfied
from a different system installation.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re

from sage.libs.gap.element import GapElement
from sage.libs.gap.libgap import libgap

__all__ = [
    "FINITE_SETS_PACKAGES",
    "GapPackage",
    "PRESENTED_MODULE_PACKAGES",
    "load_packages",
    "package_directory",
]


@dataclass(frozen=True, slots=True)
class GapPackage:
    """One exact GAP package allocated to repository execution."""

    name: str
    version: str


TOOLS_FOR_HOMALG = GapPackage("ToolsForHomalg", "2026.04-01")
MATRICES_FOR_HOMALG = GapPackage("MatricesForHomalg", "2026.04-01")
CAP = GapPackage("CAP", "2026.07-04")
MONOIDAL_CATEGORIES = GapPackage("MonoidalCategories", "2026.08-02")
CARTESIAN_CATEGORIES = GapPackage("CartesianCategories", "2026.08-02")
TOOLS_FOR_CATEGORICAL_TOWERS = GapPackage("ToolsForCategoricalTowers", "2026.08-01")
TOPOSES = GapPackage("Toposes", "2025.12-02")
FINITE_SETS = GapPackage("FinSetsForCAP", "2025.12-08")
MODULE_PRESENTATIONS = GapPackage("ModulePresentationsForCAP", "2026.06-01")

FINITE_SETS_PACKAGES = (
    TOOLS_FOR_HOMALG,
    CAP,
    MONOIDAL_CATEGORIES,
    CARTESIAN_CATEGORIES,
    TOOLS_FOR_CATEGORICAL_TOWERS,
    TOPOSES,
    FINITE_SETS,
)

PRESENTED_MODULE_PACKAGES = (
    TOOLS_FOR_HOMALG,
    MATRICES_FOR_HOMALG,
    CAP,
    MONOIDAL_CATEGORIES,
    MODULE_PRESENTATIONS,
)

_PACKAGE_NAME = re.compile(r'PackageName\s*:=\s*"([^"]+)"')
_PACKAGE_VERSION = re.compile(r'Version\s*:=\s*"([^"]+)"')


def _package_root() -> Path:
    """Return the package directory populated by ``.gap-packages.g``."""
    match "SAGE_CATEGORIES_GAP_PACKAGE_DIR" in os.environ:
        case True:
            return Path(os.environ["SAGE_CATEGORIES_GAP_PACKAGE_DIR"]).resolve()
        case False:
            return Path(__file__).resolve().parents[3] / ".gap" / "pkg"


def _package_identity(package_info: Path) -> GapPackage:
    """Read only the package name and version from GAP's metadata file."""
    text = package_info.read_text(encoding="utf-8")
    name, version = _PACKAGE_NAME.search(text), _PACKAGE_VERSION.search(text)
    assert name is not None, f"{package_info} declares no PackageName"
    assert version is not None, f"{package_info} declares no Version"
    return GapPackage(name.group(1), version.group(1))


def package_directory(package: GapPackage) -> Path:
    """Return the unique repository-local installation of ``package``."""
    root = _package_root()
    assert root.is_dir(), f"the repository GAP package directory does not exist: {root}"
    matches = tuple(
        info.parent
        for info in root.glob("*/PackageInfo.g")
        if _package_identity(info) == package
    )
    assert len(matches) == 1, (
        f"expected one repository-local {package.name} {package.version} under {root}, found {len(matches)}"
    )
    return matches[0].resolve()


def _loaded_package_info(package: GapPackage, expected_path: Path) -> GapElement:
    """Return the exact loaded package record, rejecting a substituted installation."""
    version = str(libgap.InstalledPackageVersion(package.name))
    assert version == package.version, (
        f"loaded {package.name} {version} instead of repository allocation {package.version}"
    )
    info = libgap.PackageInfo(package.name)[0]
    directories = tuple(libgap.DirectoriesPackageLibrary(package.name, ""))
    assert len(directories) == 1, (
        f"expected one active package library for {package.name}, found {len(directories)}"
    )
    installed_path = Path(str(libgap.Filename(directories[0], ""))).resolve()
    assert installed_path == expected_path, (
        f"loaded {package.name} from {installed_path}, expected {expected_path}"
    )
    return info


def load_packages(packages: tuple[GapPackage, ...]) -> tuple[GapElement, ...]:
    """Force an exact package closure, then load it in dependency order.

    The two-pass shape is essential: loading the first package is allowed to load its
    dependencies, so every dependency path must be fixed before *any* package is loaded.
    """
    paths = tuple(package_directory(package) for package in packages)
    assert len({package.name.lower() for package in packages}) == len(packages), (
        "an exact GAP package closure names one release of each package"
    )
    for package, path in zip(packages, paths, strict=True):
        libgap.SetPackagePath(package.name, str(path))
    records: list[GapElement] = []
    for package, path in zip(packages, paths, strict=True):
        loaded = libgap.LoadPackage(package.name, f"={package.version}", False)
        assert loaded == libgap.true, (
            f"failed to load {package.name} {package.version} from {path}"
        )
        records.append(_loaded_package_info(package, path))
    return tuple(records)
