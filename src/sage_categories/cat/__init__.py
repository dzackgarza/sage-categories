"""The theory of ``Cat()``: categories, functors, morphism categories, properties, shapes."""

from sage_categories.cat import category as _category

_category.bootstrap()
del _category

from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.adjunctions import Adjunctions, Equivalences
from sage_categories.cat.cones import cones as Cones, limit_cones as LimitCones
from sage_categories.cat.opposites import Op
from sage_categories.cat.total_cones import total_cones as TotalCones

__all__ = ["Adjunctions", "Cat", "Cones", "Equivalences", "Fun", "LimitCones", "Mor", "Op", "TotalCones"]
