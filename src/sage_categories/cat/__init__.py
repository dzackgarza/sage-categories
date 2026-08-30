"""The theory of ``Cat()``: categories, functors, morphism categories, properties, shapes."""

from sage_categories.cat import category as _category
from sage_categories.kernel.compiler import construct_category_singleton

_category.bootstrap(construct_category_singleton(_category.CategoryOfCategories))
del construct_category_singleton
del _category

from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.morphisms import Mor

__all__ = ["Cat", "Fun", "Mor"]
