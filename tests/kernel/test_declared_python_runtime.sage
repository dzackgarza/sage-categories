"""The declared Sage/Python runtime is the process executing repository consumers."""

import sys

from sage_categories.kernel.sage_runtime import Integer, sage_version


def test_declared_sage_python_runtime() -> None:
    assert sys.version_info[:2] == (3r, 14r)
    major, minor, *_ = sage_version.split(".")
    assert (int(major), int(minor)) >= (10r, 10r)
    assert Integer(2) + Integer(3) == 5


test_declared_sage_python_runtime()
