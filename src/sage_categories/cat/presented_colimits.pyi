from sage_categories.cat.canonical import FinitePresentedCategory as FinitePresentedCategory
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.cones import cone as cone
from sage_categories.cat.cones import cone_apex as cone_apex
from sage_categories.cat.finite_categories import finite_category as finite_category
from sage_categories.cat.finite_categories import position as position
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.opposites import opposite_morphism as opposite_morphism
from sage_categories.cat.predicates import Unknown as Unknown
from sage_categories.engines import category_limits as category_limits
from sage_categories.engines import catlab as catlab

__all__ = ["presented_colimit_in_opposite"]

def presented_colimit_in_opposite(dual_diagram: Functor) -> CategoryOfCategories.ElementType: ...
