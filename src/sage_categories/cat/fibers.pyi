from sage_categories.cat.cat_constructions import LimitSubcategory as LimitSubcategory
from sage_categories.cat.cat_constructions import limit_of_categories as limit_of_categories
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.diagrams import cospan_diagram as cospan_diagram
from sage_categories.cat.functors import Functor as Functor
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict

__all__ = ["FiberCategory", "fiber"]

class FiberCategory(LimitSubcategory):
    def __init__(self, diagram: Functor, defining_functor: Functor, base_object: CategoryOfCategories.ElementType) -> None: ...
    def defining_functor(self) -> Functor: ...
    def base_object(self) -> CategoryOfCategories.ElementType: ...
    def inclusion(self) -> Functor: ...

def fiber(defining_functor: Functor, base_object: CategoryOfCategories.ElementType) -> FiberCategory: ...
