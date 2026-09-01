from sage.rings.integer import Integer
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.cat.predicates import Predicate
from sage_categories.sets.maps import Rule
__all__ = ['PositiveIntegersCategory', 'natural_order', 'PositiveIntegers', 'NN']

class PositiveIntegerSet:

    def __call__(self, integer: int | Integer) -> PositiveIntegersCategory.ElementType:
        ...

class PositiveIntegersCategory(Category[[Rule], []]):
    ObjectType = PositiveIntegerSet

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self) -> None:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def __call__(self) -> PositiveIntegersCategory.ObjectType:
        ...
natural_order: Predicate

def PositiveIntegers() -> PositiveIntegersCategory:
    ...
NN: PositiveIntegersCategory.ObjectType
