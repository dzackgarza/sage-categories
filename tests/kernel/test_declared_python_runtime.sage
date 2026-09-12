"""The declared Sage/Python runtime is the process executing repository consumers."""

import sys

from sage.version import version as sage_version

from sage_categories.kernel.sage_runtime import Integer


def test_declared_sage_python_runtime() -> None:
    assert sys.version_info[:2] == (3, 14)
    assert sage_version == "10.9"
    assert Integer(2) + Integer(3) == 5


test_declared_sage_python_runtime()
