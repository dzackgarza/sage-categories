"""The theory of ``Cat()``: categories, functors, morphism categories, properties, shapes."""

from sage_categories.cat import category as _category

_category.bootstrap()
del _category

from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.cones import cones as Cones, limit_cones as LimitCones
from sage_categories.cat.opposites import Op

__all__ = ["Cat", "Cones", "Fun", "LimitCones", "Mor", "Op"]
