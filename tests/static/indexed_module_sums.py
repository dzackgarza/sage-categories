"""Static projection for arbitrary-index free integer modules."""

from typing import assert_type

from sage_categories.algebra import (
    indexed_free_integer_element,
    indexed_free_integer_module,
    indexed_free_integer_support,
    integer_regular_module,
    integer_scalar_monoid,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.modules import ModuleCategory


def indexed_module_types(
    indices: CategoryOfCategories.ElementType,
    module: ModuleCategory.ObjectType,
    element: CategoryOfCategories.ElementType,
) -> None:
    assert_type(integer_scalar_monoid(), CategoryOfCategories.ElementType)
    assert_type(integer_regular_module(), ModuleCategory.ObjectType)
    assert_type(indexed_free_integer_module(indices), ModuleCategory.ObjectType)
    assert_type(indexed_free_integer_element(module, {2: 3, 1000: -4}), CategoryOfCategories.ElementType)
    assert_type(indexed_free_integer_support(module, element), CategoryOfCategories.ElementType)
