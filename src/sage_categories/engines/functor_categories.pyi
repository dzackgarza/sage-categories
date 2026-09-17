from sage_categories.cat.functors import Cat as Cat
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.engines import fp_categories as fp_categories
from sage_categories.engines.gap import FUNCTOR_CATEGORIES as FUNCTOR_CATEGORIES, load_repository_package as load_repository_package
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict

def arrow_category(category: object, target: object, arrows: tuple[object, ...]):
    ...
