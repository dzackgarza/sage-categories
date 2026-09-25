"""Static consumer for the base-relative algebra owner."""

from typing import assert_type

from sage_categories.algebra.abelian import AbelianModuleTensor
from sage_categories.algebra.algebras import (
    AlgebraCategory,
    Algebras,
)
from sage_categories.cat.functors import Functor
from sage_categories.cat.modules import ModuleCategory, Modules
from sage_categories.cat.monoidal import ActionsCategory, MonoidalStructuresCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import MonoidCategory


def algebra_owner_types(
    base: MonoidCategory.ObjectType,
    context: ActionsCategory.ObjectType,
    structure: MonoidalStructuresCategory.ObjectType,
    monoid: MonoidCategory.ObjectType,
    multiplication: MorphismCategory.ObjectType,
    unit: MorphismCategory.ObjectType,
    arrow: MorphismCategory.ObjectType,
) -> None:
    modules = Modules(base, context)
    modules.select_monoidal_structure(structure)
    assert_type(modules.monoidal_structure(), MonoidalStructuresCategory.ObjectType)
    assert_type(AbelianModuleTensor(base), MonoidalStructuresCategory.ObjectType)
    algebras = Algebras(base, context)
    assert_type(algebras, AlgebraCategory)
    assert_type(Algebras(base, structure), AlgebraCategory)
    assert_type(algebras.base(), MonoidCategory.ObjectType)
    assert_type(algebras.monoid_category(), MonoidCategory)
    assert_type(algebras.monoidal_structure(), MonoidalStructuresCategory.ObjectType)
    assert_type(algebras.module_category(), ModuleCategory)
    assert_type(algebras.monoid_presentation(), Functor)
    algebra = algebras.from_monoid(monoid)
    assert_type(algebra, AlgebraCategory.ObjectType)
    assert_type(algebras.algebra(multiplication, unit), AlgebraCategory.ObjectType)
    assert_type(algebras.homomorphism(algebra, algebra, arrow), AlgebraCategory.MorphismType)
    assert_type(algebras.to_modules(), Functor)
    assert_type(algebras.U_R(), Functor)
    assert_type(algebras.to_sets(), Functor)
