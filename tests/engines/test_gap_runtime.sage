"""The live Sage GAP session uses exact repository package closures."""

from sage_categories.engines.gap import (
    FINITE_SETS_PACKAGES,
    PRESENTED_MODULE_PACKAGES,
    load_packages,
    package_directory,
)


for packages in (FINITE_SETS_PACKAGES, PRESENTED_MODULE_PACKAGES):
    expected = tuple(package_directory(package) for package in packages)
    records = load_packages(packages)
    assert tuple(str(info.Version) for info in records) == tuple(
        package.version for package in packages
    )
    assert tuple(str(info.InstallationPath).rstrip("/") for info in records) == tuple(
        str(path) for path in expected
    )
