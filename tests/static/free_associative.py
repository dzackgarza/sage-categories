"""Static projection for the infinite-rank free associative algebra consumer."""

from typing import assert_type

from sage_categories.algebra import (
    free_associative_coefficients,
    free_associative_generator,
    free_associative_product,
    free_associative_substitution,
    free_associative_underlying_module,
    free_associative_underlying_morphism,
    integer_free_associative_algebra,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.modules import ModuleCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import MonoidCategory


def free_associative_types(
    algebra: MonoidCategory.ObjectType,
    element: ModuleCategory.ElementType,
) -> None:
    assert_type(integer_free_associative_algebra(("x", "y")), MonoidCategory.ObjectType)
    assert_type(free_associative_underlying_module(algebra), ModuleCategory.ObjectType)
    assert_type(free_associative_generator(algebra, 0), ModuleCategory.ElementType)
    assert_type(free_associative_product(algebra, element, element), ModuleCategory.ElementType)
    assert_type(free_associative_coefficients(algebra, element), dict[tuple[int, ...], int])
    assert_type(free_associative_substitution(algebra, (element, element)), MorphismCategory.ObjectType)
    assert_type(free_associative_underlying_morphism(free_associative_substitution(algebra, (element, element))), MorphismCategory.ObjectType)
