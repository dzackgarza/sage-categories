from sage.rings.integer import Integer
from sage.rings.rational import Rational
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.sets.maps import Rule
__all__ = ['RationalsCategory', 'Rationals', 'QQ']

class RationalSet:

    def __call__(self, rational: int | Integer | Rational) -> RationalsCategory.ElementType:
        ...

class RationalsCategory(Category[[Rule], []]):
    ObjectType = RationalSet

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self) -> None:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def __call__(self) -> RationalsCategory.ObjectType:
        ...

def Rationals() -> RationalsCategory:
    ...
QQ: RationalsCategory.ObjectType
