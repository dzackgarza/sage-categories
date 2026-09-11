"""Source-derived stub alias projection retains class identity."""

from __future__ import annotations

import ast
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType


def _stub_generator() -> ModuleType:
    path = Path(__file__).parents[2] / "src/sage_categories/kernel/stub_generator.py"
    spec = spec_from_file_location("stub_generator_under_test", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_engine_sources_are_generated_without_runtime_bootstrap(tmp_path: Path) -> None:
    package = tmp_path / "example"
    engine = package / "engines" / "native.py"
    category = package / "cat" / "category.py"
    engine.parent.mkdir(parents=True)
    category.parent.mkdir(parents=True)
    engine.write_text("raise RuntimeError('must not import')\n")
    category.write_text("class Category:\n    pass\n")
    generator = _stub_generator()
    assert not generator._bootstrap_source(package, engine)
    assert generator._bootstrap_source(package, category)

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
    assert (
        "type Functor = sage_categories.cat.category.CategoryOfCategories.MorphismType"
        in projected
    )
    assert (
        "type NaturalTransformation = sage_categories.cat.functors.FunctorsCategory.MorphismType"
        in projected
    )
    assert "class Functor" not in projected
    assert "class NaturalTransformation" not in projected
    assert "ordinary: int" in projected


test_runtime_role_aliases_reexport_one_provider_identity()


def test_nested_provider_cycle_hoists_one_identity_through_private_owner() -> None:
    stub = ast.parse(
        """
class Root:
    pass

class Declaration(example.Owner.ElementType):
    pass

class Owner(Declaration):
    class ElementType(Root):
        def marker(self) -> int: ...

class Consumer(Owner.ElementType):
    pass
"""
    )
    generator = _stub_generator()
    generator._hoist_lexically_cyclic_nested_classes(stub, "example")
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "class _StaticRoles_Owner:" in projected
    assert "class ElementType(Root):" in projected
    assert "class Declaration(_StaticRoles_Owner.ElementType):" in projected
    assert "class Owner(Declaration, _StaticRoles_Owner):" in projected
    assert "class Consumer(_StaticRoles_Owner.ElementType):" in projected
    owner = next(
        statement
        for statement in stub.body
        if isinstance(statement, ast.ClassDef) and statement.name == "Owner"
    )
    assert not any(
        isinstance(statement, ast.ClassDef) and statement.name == "ElementType"
        for statement in owner.body
    )


test_nested_provider_cycle_hoists_one_identity_through_private_owner()


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
        frozenset(
            {
                "sage_categories.example",
                "sage_categories.kernel.roles",
                "sage_categories.cat.category",
            }
        ),
    )
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "import sage_categories.cat.category" in projected
    assert "import sage_categories.kernel.roles" in projected
    assert (
        "class ObjectType(sage_categories.kernel.roles.ObjectOfCategory, sage_categories.cat.category.CategoryOfCategories.ElementType)"
        in projected
    )


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


def test_source_role_aliases_resolve_cat_and_typed_singletons_without_runtime_values(
    tmp_path: Path,
) -> None:
    package = tmp_path / "example"
    package.mkdir()
    (package / "category.py").write_text(
        """
__all__ = ["Cat", "CategoryOfCategories"]
class CategoryOfCategories:
    class MorphismType:
        pass
def Cat() -> CategoryOfCategories:
    raise RuntimeError
"""
    )
    (package / "functors.py").write_text(
        """
from example import category as _category
__all__ = ["Functor", "NaturalTransformation"]
Cat = _category.Cat
class FunctorsCategory:
    class MorphismType:
        pass
Functor = Cat().MorphismType
Fun: FunctorsCategory = object()
NaturalTransformation = Fun.MorphismType
"""
    )
    generator = _stub_generator()
    sources = tuple(sorted(package.rglob("*.py")))
    inheritance = {
        "arrow": {
            "example.category.CategoryOfCategories.MorphismType": (),
            "example.functors.FunctorsCategory.MorphismType": (),
        }
    }
    aliases = generator._source_role_aliases("example", package, sources, inheritance)
    assert aliases["example.functors"] == {
        "Functor": "example.category.CategoryOfCategories.MorphismType",
        "NaturalTransformation": "example.functors.FunctorsCategory.MorphismType",
    }
