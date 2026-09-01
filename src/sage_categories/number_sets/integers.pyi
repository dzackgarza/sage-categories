from sage.rings.integer import Integer
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.sets.maps import Rule
__all__ = ['IntegersCategory', 'Integers', 'ZZ']

class IntegerSet:

    def __call__(self, integer: int | Integer) -> IntegersCategory.ElementType:
        ...

class IntegersCategory(Category[[Rule], []]):
    ObjectType = IntegerSet

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self) -> None:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def __call__(self) -> IntegersCategory.ObjectType:
        ...

def Integers() -> IntegersCategory:
    ...
ZZ: IntegersCategory.ObjectType
