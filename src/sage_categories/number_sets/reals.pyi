from sage.rings.integer import Integer
from sage.rings.qqbar import AlgebraicReal
from sage.rings.rational import Rational
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.sets.maps import Rule
__all__ = ['RealsCategory', 'Reals', 'RR']

class RealSet:

    def __call__(self, real: int | Integer | Rational | AlgebraicReal) -> RealsCategory.ElementType:
        ...

class RealsCategory(Category[[Rule], []]):
    ObjectType = RealSet

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self) -> None:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def __call__(self) -> RealsCategory.ObjectType:
        ...

def Reals() -> RealsCategory:
    ...
RR: RealsCategory.ObjectType
