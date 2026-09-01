import sage_categories
from sage.rings.integer import Integer
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.cat.predicates import Predicate
from sage_categories.sets.maps import Rule
__all__ = ['PositiveIntegersCategory', 'natural_order', 'PositiveIntegers', 'NN']

class PositiveIntegerSet(sage_categories.cat.properties.PropertySubcategory.ObjectType, sage_categories.sets.objects.SetObjectDeclaration, sage_categories.kernel.roles.ObjectOfCategory):

    def __call__(self, integer: int | Integer) -> PositiveIntegersCategory.ElementType:
        ...

class PositiveIntegersCategory(Category[[Rule], []]):
    ObjectType = PositiveIntegerSet

    class ElementType(sage_categories.cat.properties.PropertySubcategory.ElementType, sage_categories.sets.elements.SetElementDeclaration, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.properties.PropertySubcategory.MorphismType, sage_categories.sets.maps.SetMapDeclaration, sage_categories.kernel.roles.MorphismOfCategory):
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
