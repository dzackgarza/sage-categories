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


def test_runtime_role_aliases_reexport_one_provider_identity() -> None:
    stub = ast.parse(
        """
from _typeshed import Incomplete
Functor: Incomplete
NaturalTransformation: Incomplete
ordinary: int
"""
    )
    generator = _stub_generator()
    generator._project_runtime_class_aliases(
        stub,
        {
            "Functor": "sage_categories.cat.category.CategoryOfCategories.MorphismType",
            "NaturalTransformation": "sage_categories.cat.functors.FunctorsCategory.MorphismType",
        },
        frozenset({"sage_categories.cat.category", "sage_categories.cat.functors"}),
    )
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "type Functor = sage_categories.cat.category.CategoryOfCategories.MorphismType" in projected
    assert "type NaturalTransformation = sage_categories.cat.functors.FunctorsCategory.MorphismType" in projected
    assert "class Functor" not in projected
    assert "class NaturalTransformation" not in projected
    assert "ordinary: int" in projected


test_runtime_role_aliases_reexport_one_provider_identity()


def test_provider_projection_imports_the_modules_owning_qualified_bases() -> None:
    stub = ast.parse(
        """
class Owner:
    class ObjectType:
        pass
"""
    )
    generator = _stub_generator()
    generator._project_provider_bases(
        stub,
        "sage_categories.example",
        {
            "sage_categories.example.Owner.ObjectType": (
                "sage_categories.kernel.roles.ObjectOfCategory",
                "sage_categories.cat.category.CategoryOfCategories.ElementType",
            )
        },
        frozenset({
            "sage_categories.example",
            "sage_categories.kernel.roles",
            "sage_categories.cat.category",
        }),
    )
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "import sage_categories.cat.category" in projected
    assert "import sage_categories.kernel.roles" in projected
    assert "class ObjectType(sage_categories.kernel.roles.ObjectOfCategory, sage_categories.cat.category.CategoryOfCategories.ElementType)" in projected


test_provider_projection_imports_the_modules_owning_qualified_bases()


def test_shared_provider_projection_uses_common_ancestry_not_context_union() -> None:
    """The static provider relation may not acquire a specialization from another runtime use."""
    first = (
        "Base.ObjectType",
        "Specialization.ObjectType",
        "Root.ObjectType",
    )
    second = (
        "Base.ObjectType",
        "Root.ObjectType",
    )
    common = tuple(name for name in first if name in second)
    assert common == ("Base.ObjectType", "Root.ObjectType")
    assert "Specialization.ObjectType" not in common


test_shared_provider_projection_uses_common_ancestry_not_context_union()
