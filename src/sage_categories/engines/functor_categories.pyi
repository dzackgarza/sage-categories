from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.engines import fp_categories as fp_categories
from sage_categories.engines.gap import FUNCTOR_CATEGORIES as FUNCTOR_CATEGORIES
from sage_categories.engines.gap import load_repository_package as load_repository_package

__all__ = ["arrow_category"]

def arrow_category(category: object, target: object, arrows: tuple[object, ...]): ...
