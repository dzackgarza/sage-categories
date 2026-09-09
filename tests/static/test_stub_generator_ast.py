"""Source-derived stub alias projection retains class identity."""

from __future__ import annotations

import ast
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _stub_generator():
    path = Path(__file__).parents[2] / "src/sage_categories/kernel/stub_generator.py"
    spec = spec_from_file_location("stub_generator_under_test", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_class_aliases_bind_declared_parameters() -> None:
    source = ast.parse(
        """
class Declaration[**P, **Q]:
    pass

Category = Declaration

class Owner:
    ObjectType = Declaration
    ordinary = 3
"""
    )
    stub = ast.parse(
        """
class Declaration[**P, **Q]:
    pass

Category = Declaration

class Owner:
    ObjectType = Declaration
    ordinary = 3
"""
    )
    generator = _stub_generator()
    generator._project_class_aliases(stub, source)
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "type Category[**P, **Q] = Declaration[P, Q]" in projected
    assert "type ObjectType[**P, **Q] = Declaration[P, Q]" in projected
    assert "ordinary = 3" in projected


test_class_aliases_bind_declared_parameters()
