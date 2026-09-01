import sage_categories
from sage.rings.integer import Integer
from sage.rings.qqbar import AlgebraicReal
from sage.rings.rational import Rational
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.sets.maps import Rule
__all__ = ['RealsCategory', 'Reals', 'RR']

class RealSet(sage_categories.cat.properties.PropertySubcategory.ObjectType, sage_categories.sets.objects.SetObjectDeclaration, sage_categories.kernel.roles.ObjectOfCategory):

    def __call__(self, real: int | Integer | Rational | AlgebraicReal) -> RealsCategory.ElementType:
        ...

class RealsCategory(Category[[Rule], []]):
    ObjectType = RealSet

    class ElementType(sage_categories.cat.properties.PropertySubcategory.ElementType, sage_categories.sets.elements.SetElementDeclaration, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.properties.PropertySubcategory.MorphismType, sage_categories.sets.maps.SetMapDeclaration, sage_categories.kernel.roles.MorphismOfCategory):
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
