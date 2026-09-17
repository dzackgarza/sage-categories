"""Static endpoints for decisive relative-algebra consumers."""

from typing import assert_type

from sage_categories.algebra.algebras import AlgebraCategory
from sage_categories.cat.functors import Functor
from sage_categories.cat.modules import ModuleCategory
from sage_categories.cat.monoidal import MonoidalStructuresCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import MonoidCategory


def relative_algebra_consumer_types(
    algebras: AlgebraCategory,
    algebra: AlgebraCategory.ObjectType,
    monoid: MonoidCategory.ObjectType,
) -> None:
    assert_type(algebra, AlgebraCategory.ObjectType)
    assert_type(algebras.base(), MonoidCategory.ObjectType)
    assert_type(algebras.monoidal_structure(), MonoidalStructuresCategory.ObjectType)
    assert_type(algebras.module_category(), ModuleCategory)
    assert_type(algebras.monoid_presentation(), Functor)
    assert_type(algebras.to_modules(), Functor)
    assert_type(algebras.from_monoid(monoid), AlgebraCategory.ObjectType)
    assert_type(monoid.operation(), MorphismCategory.ObjectType)
    assert_type(monoid.unit_morphism(), MorphismCategory.ObjectType)
