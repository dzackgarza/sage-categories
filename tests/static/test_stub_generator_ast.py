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
    assert "type Functor = sage_categories.cat.category.CategoryOfCategories.MorphismType" in projected
    assert "type NaturalTransformation = sage_categories.cat.functors.FunctorsCategory.MorphismType" in projected
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
    owner = next(statement for statement in stub.body if isinstance(statement, ast.ClassDef) and statement.name == "Owner")
    assert not any(isinstance(statement, ast.ClassDef) and statement.name == "ElementType" for statement in owner.body)


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
        {},
    )
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "import sage_categories.cat.category" in projected
    assert "import sage_categories.kernel.roles" in projected
    assert "class ObjectType(sage_categories.kernel.roles.ObjectOfCategory, sage_categories.cat.category.CategoryOfCategories.ElementType)" in projected


test_provider_projection_imports_the_modules_owning_qualified_bases()


def test_provider_projection_uses_direct_hoisted_role_typeinfo() -> None:
    stub = ast.parse(
        """
class ObjectType:
    pass
"""
    )
    generator = _stub_generator()
    public = "sage_categories.cat.category.CategoryOfCategories.MorphismType"
    helper = "sage_categories.cat.category._StaticRoles_CategoryOfCategories.MorphismType"
    generator._project_provider_bases(
        stub,
        "sage_categories.example",
        {"sage_categories.example.ObjectType": (public,)},
        frozenset({"sage_categories.example", "sage_categories.cat.category"}),
        {public: helper},
    )
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert f"class ObjectType({helper}):" in projected


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
        """
__all__ = ["public"]

def public() -> int:
    return 1

def internal() -> str:
    return "internal"

def _private() -> bool:
    return True
"""
    )
    (package / "direct.py").write_text("from example.owner import internal\n")
    (package / "qualified.py").write_text("from example import owner\nresult = owner._private()\n")
    generator = _stub_generator()
    sources = tuple(sorted(package.rglob("*.py")))
    assert generator._internal_static_names("example", package, sources)["example.owner"] == frozenset({"internal", "_private"})


def test_internal_static_projection_keeps_runtime_exports_separate() -> None:
    stub = ast.parse(
        """
from example.types import PublicType
__all__ = ["public"]
def public() -> PublicType: ...
"""
    )
    private_stub = ast.parse(
        """
from example.types import PublicType, InternalType
__all__ = ["public"]
def public() -> PublicType: ...
class _InternalRecord: ...
def internal(value: InternalType) -> _InternalRecord: ...
def _private() -> bool: ...
"""
    )
    generator = _stub_generator()
    generator._project_internal_definitions(stub, private_stub, frozenset({"internal", "_private"}))
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert generator._public_names(stub) == ("public",)
    assert "class _InternalRecord:" in projected
    assert "def internal(value: InternalType) -> _InternalRecord:" in projected
    assert "def _private() -> bool:" in projected
    assert "from example.types import InternalType" in projected


def test_refresh_internal_static_definitions_updates_only_internal_surface(
    tmp_path: Path,
) -> None:
    package = tmp_path / "example"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "owner.py").write_text(
        """
__all__ = ["public"]

def public() -> int:
    return 1

def internal() -> str:
    return "internal"
"""
    )
    (package / "consumer.py").write_text("from example.owner import internal\n")
    (package / "__init__.pyi").write_text("")
    (package / "owner.pyi").write_text('__all__ = ["public"]\ndef public() -> int: ...\n')
    (package / "consumer.pyi").write_text("from example.owner import internal as internal\n")
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
        "example.MorphismCategory.ObjectType": ("example.Root.ElementType",),
    }
    assert generator._direct_provider_bases(relations["example.Owner.MorphismType"], relations) == (
        "sage_categories.kernel.roles.MorphismOfCategory",
        "example.MorphismCategory.ObjectType",
    )
    assert generator._providers_in_module({"arrow": relations}, "example")["example.Owner.MorphismType"] == (
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
    assert generator._providers_in_module(inheritance, "example")["example.FunctorObject"] == ("example.CatMorphism",)


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


def test_category_role_projection_is_noop_without_category_declarations() -> None:
    source = ast.parse("def helper(value: int) -> int:\n    return value\n")
    stub = ast.parse("def helper(value: int) -> int: ...\n")
    before = ast.dump(stub, include_attributes=False)
    generator = _stub_generator()
    generator._project_category_role_parameters(
        stub,
        source,
        "example",
        {},
        {},
        frozenset(),
        {},
        frozenset({"example", "sage_categories.kernel.roles"}),
    )
    assert ast.dump(stub, include_attributes=False) == before


def test_category_role_hoisting_keeps_role_only_owner_syntactic() -> None:
    source = ast.parse(
        """
class CategoryDeclaration[**P, **Q, ObjectRole=object, ElementRole=object, MorphismRole=object]:
    pass
Category = CategoryDeclaration

class RoleOnly(Category):
    class ObjectType: pass
    class ElementType: pass
    class MorphismType: pass
"""
    )
    stub = ast.parse(ast.unparse(source))
    generator = _stub_generator()
    counts = {"CategoryDeclaration": 2, "Category": 2, "RoleOnly": 0}
    generator._project_class_aliases(stub, source)
    generator._project_category_role_parameters(
        stub,
        source,
        "example",
        counts,
        {"RoleOnly": "example"},
        frozenset(),
        {},
        frozenset({"example", "sage_categories.kernel.roles"}),
    )
    projected = ast.unparse(ast.fix_missing_locations(stub))
    ast.parse(projected)
    assert "class RoleOnly" in projected
    assert "pass" in projected


def test_category_roles_are_hidden_parameters_threaded_through_base() -> None:
    source = ast.parse(
        """
class CategoryDeclaration[**P, **Q, ObjectRole=object, ElementRole=object, MorphismRole=object]:
    pass
Category = CategoryDeclaration

class Base[**P, **Q](Category[P, Q]):
    class ObjectType: pass
    class ElementType: pass
    class MorphismType: pass
    def construct(self, value: Base.ObjectType) -> Base.MorphismType: ...

class Derived(Base):
    class ObjectType: pass
    class ElementType: pass
    class MorphismType: pass
    def construct(self, value: Derived.ObjectType) -> Derived.MorphismType: ...
"""
    )
    stub = ast.parse(ast.unparse(source))
    generator = _stub_generator()
    counts = {"CategoryDeclaration": 2, "Category": 2, "Base": 2, "Derived": 0}
    generator._project_class_aliases(stub, source)
    generator._project_category_role_parameters(
        stub,
        source,
        "example",
        counts,
        {"Base": "example", "Derived": "example"},
        frozenset({"Base"}),
        {},
        frozenset({"example", "sage_categories.kernel.roles"}),
    )
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "ObjectRole = object" in projected
    assert "ElementRole = object" in projected
    assert "MorphismRole = object" in projected
    assert "class _StaticRoles_Base:" in projected
    assert "Category[P, Q, _ObjectRole, _ElementRole, _MorphismRole]" in projected
    assert "_CategoryDeclaration_ObjectRole = _typing.TypeVar" in projected
    assert "_ObjectRole = _StaticRoles_Base.ObjectType" in projected
    assert "def construct(self, value: _ObjectRole) -> _MorphismRole:" in projected
    assert "class _StaticRoles_Derived(_StaticRoles_Base):" in projected
    assert "class Derived" in projected
    assert "_StaticRoles_Derived, Base[..., ..., _StaticRoles_Derived.ObjectType, _StaticRoles_Derived.ElementType, _StaticRoles_Derived.MorphismType]" in projected
    assert "class Derived[_ObjectRole" not in projected


def test_category_role_projection_replaces_existing_hidden_base_roles() -> None:
    source = ast.parse(
        """
class CategoryDeclaration[**P, **Q, ObjectRole=object, ElementRole=object, MorphismRole=object]:
    pass
Category = CategoryDeclaration

class Base[**P, **Q, _ObjectRole=object, _ElementRole=object, _MorphismRole=object](
    Category[P, Q, _ObjectRole, _ElementRole, _MorphismRole]
):
    class ObjectType: pass
    class ElementType: pass
    class MorphismType: pass

class Derived(Base):
    class ObjectType: pass
    class ElementType: pass
    class MorphismType: pass
"""
    )
    stub = ast.parse(ast.unparse(source))
    generator = _stub_generator()
    counts = {"CategoryDeclaration": 2, "Category": 2, "Base": 2, "Derived": 0}
    generator._project_class_aliases(stub, source)

    generator._project_category_role_parameters(
        stub,
        source,
        "example",
        counts,
        {"Base": "example", "Derived": "example"},
        frozenset({"Base"}),
        {},
        frozenset({"example", "sage_categories.kernel.roles"}),
    )

    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "Category[P, Q, _ObjectRole, _ElementRole, _MorphismRole]" in projected
    assert "Category[P, Q, _ObjectRole, _ElementRole, _MorphismRole, _ObjectRole" not in projected


def test_public_exports_ignore_stubgen_function_local_classes() -> None:
    source = ast.parse(
        """
__all__ = ["public"]

def public() -> None:
    class _Local:
        pass
"""
    )
    stub = ast.parse(
        """
__all__ = ["public", "_Local@5"]

def public() -> None: ...
"""
    )
    generator = _stub_generator()

    generator._project_public_exports(stub, source)

    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "__all__ = ['public']" in projected
    assert "_Local@5" not in projected


def test_category_role_genericity_crosses_module_boundaries(tmp_path: Path) -> None:
    base = tmp_path / "base.py"
    derived = tmp_path / "derived.py"
    base.write_text(
        """
class Base:
    class ObjectType: pass
    class ElementType: pass
    class MorphismType: pass
"""
    )
    derived.write_text(
        """
from base import Base

class Derived(Base):
    class ObjectType: pass
    class ElementType: pass
    class MorphismType: pass
"""
    )
    generator = _stub_generator()

    generic_bases = generator._source_generic_category_bases((base, derived), {"Base": 0, "Derived": 0})

    assert generic_bases == frozenset({"Base"})


def test_category_parameter_counts_include_public_endpoint_typevars(tmp_path: Path) -> None:
    source = tmp_path / "fixed.py"
    source.write_text(
        """
class Fixed[
    **P,
    **Q,
    DomainType=object,
    CodomainType=object,
    ObjectRole=object,
    ElementRole=object,
    MorphismRole=object,
]:
    class ObjectType: pass
    class ElementType: pass
    class MorphismType: pass
"""
    )
    generator = _stub_generator()

    counts = generator._source_category_parameter_counts((source,))

    assert counts["Fixed"] == 4


def test_hoisted_role_provider_keeps_source_generic_parameters() -> None:
    generator = _stub_generator()
    public = "example.Owner.ObjectType"
    helper = "example._StaticRoles_Owner.ObjectType"

    parameters = generator._include_hoisted_role_parameters(
        {public: ("Domain", "Codomain")},
        {public: helper},
    )

    assert parameters[helper] == ("Domain", "Codomain")


def test_generic_role_specializes_matching_provider_base() -> None:
    source = ast.parse(
        """
class CategoryDeclaration[**P, **Q, ObjectRole=object, ElementRole=object, MorphismRole=object]:
    pass
Category = CategoryDeclaration

class Provider[A, B]:
    pass

class Owner[A=object, B=object](Category):
    class ObjectType[A=object, B=object]: pass
    class ElementType: pass
    class MorphismType: pass
"""
    )
    stub = ast.parse(ast.unparse(source))
    owner = next(statement for statement in stub.body if isinstance(statement, ast.ClassDef) and statement.name == "Owner")
    object_type = next(statement for statement in owner.body if isinstance(statement, ast.ClassDef) and statement.name == "ObjectType")
    generator = _stub_generator()
    object_type.bases = [generator._base_expression("example.Provider")]
    counts = {"CategoryDeclaration": 2, "Category": 2, "Owner": 2}
    generator._project_class_aliases(stub, source)

    generator._project_category_role_parameters(
        stub,
        source,
        "example",
        counts,
        {"Owner": "example"},
        frozenset(),
        {
            "example.Provider": ("A", "B"),
            "example.Owner.ObjectType": ("A", "B"),
        },
        frozenset({"example", "sage_categories.kernel.roles"}),
    )

    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "class ObjectType[A = object, B = object](example.Provider[A, B])" in projected
    assert "_StaticRoles_Owner.ObjectType[A, B]" in projected


def test_hoisted_role_defaults_resolve_to_direct_typeinfo() -> None:
    stub = ast.parse(
        """
import typing as _typing
class Carrier[T = "Owner.ObjectType"]:
    pass
_AliasRole = _typing.TypeVar("_AliasRole", default="Owner.ObjectType")
"""
    )
    generator = _stub_generator()
    helper = "example._StaticRoles_Owner.ObjectType"

    generator._project_hoisted_role_defaults(
        stub,
        "example",
        {"example.Owner.ObjectType": helper},
    )

    projected = ast.unparse(ast.fix_missing_locations(stub))
    local_helper = "_StaticRoles_Owner.ObjectType"
    assert f"class Carrier[T = {local_helper}]" in projected
    assert f"default={local_helper}" in projected


def test_generic_morphism_projection_uses_declared_endpoint_parameters() -> None:
    stub = ast.parse(
        """
class Owner:
    class ObjectType: pass
    class MorphismType[DomainCategory, CodomainCategory]: pass
"""
    )
    generator = _stub_generator()

    generator._project_exact_morphism_endpoints(stub)

    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "def domain(self) -> DomainCategory:" in projected
    assert "def codomain(self) -> CodomainCategory:" in projected


def test_public_static_surface_keeps_export_signature_dependencies() -> None:
    source = ast.parse(
        """
__all__ = ["public"]
type Support = int
def public(value: Support) -> Support: ...
def hidden() -> str: ...
"""
    )
    stub = ast.parse(ast.unparse(source))
    generator = _stub_generator()

    generator._project_public_static_surface(stub, source)

    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "type Support = int" in projected
    assert "def public(value: Support) -> Support:" in projected
    assert "def hidden()" not in projected


def test_source_value_alias_projection_restores_module_reexport() -> None:
    source = ast.parse(
        """
from example import owner as _owner
__all__ = ["Public"]
Public = _owner.Public
"""
    )
    stub = ast.parse(
        """
from _typeshed import Incomplete
Public: Incomplete
"""
    )
    generator = _stub_generator()

    generator._project_source_value_aliases(stub, source)

    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "from example.owner import Public as Public" in projected
    assert "Public: Incomplete" not in projected


def test_category_role_projection_restores_source_role_alias_lost_by_parse_only() -> None:
    source = ast.parse(
        """
class CategoryDeclaration[**P, **Q, ObjectRole=object, ElementRole=object, MorphismRole=object]:
    pass
Category = CategoryDeclaration

class Base:
    class MorphismType: pass

class Owner(Category):
    ObjectType = Base.MorphismType
    class ElementType: pass
    class MorphismType: pass
"""
    )
    stub = ast.parse(
        """
from _typeshed import Incomplete
class CategoryDeclaration[**P, **Q]: pass
Category = CategoryDeclaration
class Base:
    class MorphismType: pass
class Owner(Category):
    ObjectType: Incomplete
    class ElementType: pass
    class MorphismType: pass
"""
    )
    generator = _stub_generator()
    generator._project_class_aliases(stub, source)

    generator._project_category_role_parameters(
        stub,
        source,
        "example",
        {"CategoryDeclaration": 2, "Category": 2, "Owner": 0},
        {"Owner": "example"},
        frozenset(),
        {},
        frozenset({"example", "sage_categories.kernel.roles"}),
    )

    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "ObjectType = Base.MorphismType" in projected
    assert "ObjectType: Incomplete" not in projected


def test_role_local_generics_do_not_require_category_owner_parameters() -> None:
    source = ast.parse(
        """
class CategoryDeclaration[**P, **Q, ObjectRole=object, ElementRole=object, MorphismRole=object]:
    pass
Category = CategoryDeclaration

class Owner(Category):
    class ObjectType: pass
    class ElementType: pass
    class MorphismType[Local=object]: pass
"""
    )
    stub = ast.parse(ast.unparse(source))
    generator = _stub_generator()
    generator._project_class_aliases(stub, source)

    generator._project_category_role_parameters(
        stub,
        source,
        "example",
        {"CategoryDeclaration": 2, "Category": 2, "Owner": 0},
        {"Owner": "example"},
        frozenset(),
        {"example.Owner.MorphismType": ("Local",)},
        frozenset({"example", "sage_categories.kernel.roles"}),
    )

    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "class MorphismType[Local = object]" in projected
    assert "_StaticRoles_Owner.MorphismType[Local]" not in projected
    assert "_StaticRoles_Owner.MorphismType" in projected


def test_source_value_alias_projection_restores_public_import_alias() -> None:
    source = ast.parse(
        """
from example.owner import public as Public
__all__ = ["Public"]
"""
    )
    stub = ast.parse("")
    generator = _stub_generator()

    generator._project_source_value_aliases(stub, source)

    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "from example.owner import public as Public" in projected


def test_quoted_type_parameter_projection_preserves_forward_references() -> None:
    source = ast.parse(
        """
class Owner:
    class Role[T: "Owner" = "Owner"]: pass

class Family[T = "Owner"]: pass
"""
    )
    stub = ast.parse(
        """
class Owner:
    class Role[T: Owner = Owner]: pass

class Family[T = Owner]: pass
"""
    )
    generator = _stub_generator()

    generator._project_quoted_type_parameter_references(stub, source, "example")

    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "class Role[T: 'Owner' = 'Owner']" in projected
    assert "class Family[T = 'Owner']" in projected


def test_projector_renders_with_formatter_before_writing(tmp_path: Path) -> None:
    stub = tmp_path / "category.pyi"
    stub.write_text("sentinel\n")
    config = tmp_path / "ruff.toml"
    config.write_text('line-length = 176\ntarget-version = "py314"\n')
    generator = _stub_generator()

    rendered = generator._render_stub_source(
        ast.parse("class Category: ...\n"),
        "sage_categories",
        stub,
        config,
    )

    assert rendered == "class Category: ...\n"
    assert stub.read_text() == "sentinel\n"


def test_projection_scope_removes_stubs_for_ordinary_modules(tmp_path: Path) -> None:
    package = tmp_path / "example"
    package.mkdir()
    (package / "category.pyi").write_text("class Category: ...\n")
    (package / "ordinary.pyi").write_text("def value() -> int: ...\n")
    generator = _stub_generator()

    generator._remove_non_projection_stubs(
        "example",
        package,
        frozenset({"example.category"}),
    )

    assert (package / "category.pyi").exists()
    assert not (package / "ordinary.pyi").exists()


def test_stub_import_groups_prune_stale_incomplete_and_sort_project_imports() -> None:
    tree = ast.parse(
        """
import sage_categories.kernel.roles
from _typeshed import Incomplete
from dataclasses import dataclass
from sage.structure.parent import Parent
from sage_categories.cat.category import Category as Category, Cat as Cat

class Owner:
    value: Category
"""
    )
    generator = _stub_generator()
    groups = generator._stub_import_groups(tree, "sage_categories")
    rendered = [[ast.unparse(statement) for statement in group] for group in groups]
    assert rendered == [
        [
            "import sage_categories.kernel.roles",
            "from sage_categories.cat.category import Cat as Cat",
            "from sage_categories.cat.category import Category as Category",
        ],
    ]


def test_stub_import_groups_retain_incomplete_when_projection_uses_it() -> None:
    tree = ast.parse(
        """
from _typeshed import Incomplete
import sage_categories.kernel.roles

value: Incomplete
"""
    )
    generator = _stub_generator()
    groups = generator._stub_import_groups(tree, "sage_categories")
    rendered = [[ast.unparse(statement) for statement in group] for group in groups]
    assert rendered == [
        ["from _typeshed import Incomplete"],
        ["import sage_categories.kernel.roles"],
    ]


def test_final_projection_marks_owned_generic_aliases() -> None:
    source = ast.parse(
        """
class Declaration[**P]:
    pass

Category = Declaration
"""
    )
    stub = ast.parse(
        """
class Declaration[**P]:
    pass

Category = Declaration
"""
    )
    generator = _stub_generator()
    projected_aliases = generator._project_class_aliases(stub, source)
    generator._mark_projected_generic_aliases(stub, projected_aliases)
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "Category: _typing.TypeAlias = Declaration[_Declaration_P,]" in projected


def test_final_projection_publicizes_class_local_type_parameters() -> None:
    stub = ast.parse(
        """
class Carrier[_ObjectRole = object, _MorphismRole = object]:
    def construct(self, value: _ObjectRole) -> _MorphismRole: ...
"""
    )
    generator = _stub_generator()
    generator._publicize_private_type_parameters(stub)
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "class Carrier[ObjectRole = object, MorphismRole = object]" in projected
    assert "def construct(self, value: ObjectRole) -> MorphismRole" in projected
    assert "_ObjectRole" not in projected
    assert "_MorphismRole" not in projected


def test_final_projection_unquotes_forward_refs_but_preserves_literal_values() -> None:
    stub = ast.parse(
        """
from typing import Literal

type Alias = tuple["Owner", Literal["tag"]]
class Carrier[T: "Owner" = "Owner"]:
    def construct(self, value: "Owner") -> "Owner": ...
"""
    )
    generator = _stub_generator()
    generator._unquote_stub_annotations(stub)
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "type Alias = tuple[Owner, Literal['tag']]" in projected
    assert "class Carrier[T: Owner = Owner]" in projected
    assert "def construct(self, value: Owner) -> Owner" in projected


def test_final_projection_normalizes_stub_class_bodies() -> None:
    stub = ast.parse(
        """
class NonEmpty:
    ...
    value: int

class Empty:
    pass
"""
    )
    generator = _stub_generator()
    generator._normalize_stub_class_bodies(stub)
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "class NonEmpty:\n    value: int" in projected
    assert "class Empty:\n    ..." in projected


def test_final_projection_localizes_self_references() -> None:
    stub = ast.parse(
        """
import example.category
import example.other

class Carrier(example.category.Base):
    value: example.category.Role
"""
    )
    generator = _stub_generator()
    generator._localize_self_references(stub, "example.category")
    projected = ast.unparse(ast.fix_missing_locations(stub))
    assert "import example.category" not in projected
    assert "import example.other" in projected
    assert "class Carrier(Base)" in projected
    assert "value: Role" in projected
