from sage_categories.cat.adjunctions import Equivalences as Equivalences
from sage_categories.cat.adjunctions import EquivalencesCategory as EquivalencesCategory
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import FunctorCategory as FunctorCategory
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.opposites import opposite_morphism as opposite_morphism
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function

__all__ = ["dual_functor_category_equivalence"]

def dual_functor_category_equivalence(shape: Category, target: Category) -> EquivalencesCategory.ObjectType: ...
