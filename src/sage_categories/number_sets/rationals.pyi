import sage_categories
from sage.rings.integer import Integer
from sage.rings.rational import Rational
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.sets.maps import Rule
__all__ = ['RationalsCategory', 'Rationals', 'QQ']

class RationalSet(sage_categories.cat.properties.PropertySubcategory.ObjectType, sage_categories.sets.objects.SetObjectDeclaration, sage_categories.kernel.roles.ObjectOfCategory):

    def __call__(self, rational: int | Integer | Rational) -> RationalsCategory.ElementType:
        ...

class RationalsCategory(Category[[Rule], []]):
    ObjectType = RationalSet

    class ElementType(sage_categories.cat.properties.PropertySubcategory.ElementType, sage_categories.sets.elements.SetElementDeclaration, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.properties.PropertySubcategory.MorphismType, sage_categories.sets.maps.SetMapDeclaration, sage_categories.kernel.roles.MorphismOfCategory):
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
