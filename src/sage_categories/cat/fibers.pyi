from sage_categories.cat.cat_constructions import LimitCategory
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor
__all__ = ['FiberCategory', 'fiber']

class FiberCategory(LimitCategory):

    def __init__(self, diagram: Functor, defining_functor: Functor, base_object: CategoryOfCategories.ElementType) -> None:
        ...

    def defining_functor(self) -> Functor:
        ...

    def base_object(self) -> CategoryOfCategories.ElementType:
        ...

    def inclusion(self) -> Functor:
        ...

def fiber(defining_functor: Functor, base_object: CategoryOfCategories.ElementType) -> FiberCategory:
    ...
