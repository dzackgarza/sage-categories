"""Static consumer for the base-relative algebra owner."""

from typing import assert_type

from sage_categories.algebra.abelian import AbelianModuleTensor
from sage_categories.algebra.algebras import (
    AlgebraCategory,
    Algebras,
)
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.cat.modules import ModuleCategory, Modules
from sage_categories.cat.monoidal import ActionsCategory, MonoidalStructuresCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import MonoidCategory


def algebra_owner_types[BaseScalar: MonoidCategory.ObjectType](
    base: BaseScalar,
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
    module_tensor = AbelianModuleTensor(base)
    assert_type(
        module_tensor.underlying_category(),
        ModuleCategory[BaseScalar, Category, Category],
    )
    algebras = Algebras(base, context)
    assert_type(algebras, AlgebraCategory[BaseScalar])
    assert_type(Algebras(base, structure), AlgebraCategory[BaseScalar])
    assert_type(algebras.base(), BaseScalar)
    assert_type(algebras.monoid_category(), MonoidCategory)
    assert_type(algebras.monoidal_structure(), MonoidalStructuresCategory.ObjectType)
    assert_type(algebras.module_category(), ModuleCategory[BaseScalar])
    presentation = algebras.monoid_presentation()
    assert_type(presentation.codomain(), MonoidCategory)
    algebra = algebras.from_monoid(monoid)
    assert_type(presentation.on_object(algebra), MonoidCategory.ObjectType)
    assert_type(algebra, AlgebraCategory.ObjectType)
    assert_type(algebras.algebra(multiplication, unit), AlgebraCategory.ObjectType)
    assert_type(algebras.homomorphism(algebra, algebra, arrow), AlgebraCategory.MorphismType)
    to_modules = algebras.to_modules()
    assert_type(to_modules.codomain(), ModuleCategory[BaseScalar])
    assert_type(to_modules.on_object(algebra), ModuleCategory.ObjectType)
    assert_type(to_modules.on_morphism(algebras.homomorphism(algebra, algebra, arrow)), ModuleCategory.MorphismType)
    assert_type(algebras.U_R(), Functor)
    assert_type(algebras.functor_to_sets(), Functor)
