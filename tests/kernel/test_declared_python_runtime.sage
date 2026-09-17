"""The declared Sage/Python runtime is the process executing repository consumers."""

import sys

from sage_categories.kernel.sage_runtime import Integer, sage_version


def test_declared_sage_python_runtime() -> None:
    assert sys.version_info[:2] == (3, 14)
    major, minor, *_ = sage_version.split(".")
    assert (int(major), int(minor)) >= (10, 10)
    assert Integer(2) + Integer(3) == 5


test_declared_sage_python_runtime()
