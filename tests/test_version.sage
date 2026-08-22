"""The package imports under Sage and reports this tree's declared version."""

import tomllib
from pathlib import Path

import sage_categories

# QC preparses this file into a tempdir, so __file__ says nothing about where
# the repository is. The editable install does: sage_categories.__file__
# points back into this tree, so the version pyproject declares is readable
# from the tree that produced the install being tested.
#
# Walked with .parent rather than parents[2]: the Sage preparser rewrites the
# integer literal to Integer(2), which Path.parents does not accept.
REPO_ROOT = Path(sage_categories.__file__).resolve().parent.parent.parent


def test_package_reports_the_version_declared_in_pyproject() -> None:
    """The runtime version is the one this tree declares.

    Reaching this assertion proves the package imports under Sage's own
    Python. The assertion then proves the installed distribution matches the
    tree, so a stale install fails here rather than reporting an old version.
    """
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    assert sage_categories.version() == pyproject["project"]["version"]
