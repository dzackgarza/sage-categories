from sage_categories.cat.adjunctions import EquivalencesCategory
from sage_categories.cat.category import Category
__all__ = ['dual_functor_category_equivalence']

def dual_functor_category_equivalence(shape: Category, target: Category) -> EquivalencesCategory.ObjectType:
    ...
