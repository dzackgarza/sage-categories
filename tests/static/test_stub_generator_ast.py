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
    assert "Category = Declaration[_Declaration_P, _Declaration_Q]" in projected
    assert "ObjectType = Declaration[_Declaration_P, _Declaration_Q]" in projected
    assert "_Declaration_P = _typing.ParamSpec('_Declaration_P')" in projected
    assert "_Declaration_Q = _typing.ParamSpec('_Declaration_Q')" in projected
    assert "ordinary = 3" in projected
    generator._project_class_aliases(stub, source)
    assert ast.unparse(ast.fix_missing_locations(stub)) == projected


def test_class_aliases_convert_existing_pep695_projection() -> None:
    source = ast.parse(
        """
class Declaration[**P, **Q]:
    pass

Category = Declaration

class Owner:
    ObjectType = Declaration
"""
    )
    stub = ast.parse(
        """
class Declaration[**P, **Q]:
    pass

type Category[**P, **Q] = Declaration[P, Q]

class Owner:
    type ObjectType[**P, **Q] = Declaration[P, Q]
"""
    )
    generator = _stub_generator()
    generator._project_class_aliases(stub, source)
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "type Category" not in projected
    assert "type ObjectType" not in projected
    assert "Category = Declaration[_Declaration_P, _Declaration_Q]" in projected
    assert "ObjectType = Declaration[_Declaration_P, _Declaration_Q]" in projected


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


def test_internal_static_names_follow_explicit_cross_module_use(tmp_path: Path) -> None:
    package = tmp_path / "example"
    package.mkdir()
    (package / "__init__.py").write_text("from . import owner\n")
    (package / "owner.py").write_text(
        '''
__all__ = ["public"]

def public() -> int:
    return 1

def internal() -> str:
    return "internal"

def _private() -> bool:
    return True
'''
    )
    (package / "direct.py").write_text("from example.owner import internal\n")
    (package / "qualified.py").write_text(
        "from example import owner\nresult = owner._private()\n"
    )
    generator = _stub_generator()
    sources = tuple(sorted(package.rglob("*.py")))
    assert generator._internal_static_names("example", package, sources)[
        "example.owner"
    ] == frozenset({"internal", "_private"})


def test_internal_static_projection_keeps_runtime_exports_separate() -> None:
    stub = ast.parse(
        '''
from example.types import PublicType
__all__ = ["public"]
def public() -> PublicType: ...
'''
    )
    private_stub = ast.parse(
        '''
from example.types import PublicType, InternalType
__all__ = ["public"]
def public() -> PublicType: ...
def internal(value: InternalType) -> InternalType: ...
def _private() -> bool: ...
'''
    )
    generator = _stub_generator()
    generator._project_internal_definitions(
        stub, private_stub, frozenset({"internal", "_private"})
    )
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert generator._public_names(stub) == ("public",)
    assert "def internal(value: InternalType) -> InternalType:" in projected
    assert "def _private() -> bool:" in projected
    assert "from example.types import InternalType" in projected


def test_refresh_internal_static_definitions_updates_only_internal_surface(
    tmp_path: Path,
) -> None:
    package = tmp_path / "example"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "owner.py").write_text(
        '''
__all__ = ["public"]

def public() -> int:
    return 1

def internal() -> str:
    return "internal"
'''
    )
    (package / "consumer.py").write_text("from example.owner import internal\n")
    (package / "__init__.pyi").write_text("")
    (package / "owner.pyi").write_text(
        '__all__ = ["public"]\ndef public() -> int: ...\n'
    )
    (package / "consumer.pyi").write_text(
        "from example.owner import internal as internal\n"
    )
    generator = _stub_generator()
    sources = tuple(sorted(package.rglob("*.py")))
    generator._refresh_internal_static_definitions("example", package, sources)
    projected = ast.parse((package / "owner.pyi").read_text())
    assert generator._public_names(projected) == ("public",)
    assert "def internal() -> str:" in ast.unparse(projected)


def test_provider_projection_uses_direct_branches_not_transitive_c3_ancestry() -> None:
    generator = _stub_generator()
    relations = {
        "example.Owner.MorphismType": (
            "example.Root.ElementType",
            "sage_categories.kernel.roles.MorphismOfCategory",
            "example.MorphismCategory.ObjectType",
        ),
        "example.MorphismCategory.ObjectType": (
            "example.Root.ElementType",
        ),
    }
    assert generator._direct_provider_bases(
        relations["example.Owner.MorphismType"], relations
    ) == (
        "sage_categories.kernel.roles.MorphismOfCategory",
        "example.MorphismCategory.ObjectType",
    )
    assert generator._providers_in_module(
        {"arrow": relations}, "example"
    )["example.Owner.MorphismType"] == (
        "sage_categories.kernel.roles.MorphismOfCategory",
        "example.MorphismCategory.ObjectType",
    )



def test_provider_projection_prunes_ancestry_across_role_surfaces() -> None:
    generator = _stub_generator()
    inheritance = {
        "object": {
            "example.FunctorObject": (
                "example.CatMorphism",
                "example.CatElement",
                "example.ObjectRole",
            ),
        },
        "arrow": {
            "example.CatMorphism": (
                "example.GenericMorphism",
                "example.CatElement",
                "example.MorphismRole",
                "example.ObjectRole",
            ),
            "example.GenericMorphism": (
                "example.CatElement",
                "example.MorphismRole",
                "example.ObjectRole",
            ),
            "example.MorphismRole": ("example.ObjectRole",),
        },
        "element": {
            "example.CatElement": (),
        },
    }
    assert generator._providers_in_module(inheritance, "example")[
        "example.FunctorObject"
    ] == ("example.CatMorphism",)


test_provider_projection_prunes_ancestry_across_role_surfaces()

def test_concrete_morphism_projection_has_exact_owner_object_endpoints() -> None:
    stub = ast.parse(
        """
class CategoryOfCategories:
    type ObjectType = Category
    class MorphismType(MorphismOfCategory):
        def on_object(self, value: ObjectType) -> ObjectType: ...

class OwnEndpoints:
    class ObjectType:
        pass
    class MorphismType(MorphismOfCategory):
        def domain(self) -> ObjectType: ...
"""
    )
    generator = _stub_generator()
    generator._project_exact_morphism_endpoints(stub)
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "def domain(self) -> CategoryOfCategories.ObjectType:" in projected
    assert "def codomain(self) -> CategoryOfCategories.ObjectType:" in projected
    assert projected.count("def domain(self) -> OwnEndpoints.ObjectType:") == 0
    assert "def domain(self) -> ObjectType:" in projected
    assert "def codomain(self) -> OwnEndpoints.ObjectType:" in projected
