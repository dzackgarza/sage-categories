import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
__all__ = ['DeclaredCategory', 'CategoryFamily', 'Sets', 'Posets', 'Groupoids', 'TotallyOrderedSets', 'NN', 'ZZ', 'omega', 'MagmaObjects', 'MonoidObjects', 'SemiringObjects', 'RingObjects']

class _StaticRoles_DeclaredCategory:

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> DeclaredCategory.ObjectType:
            ...

        def codomain(self) -> DeclaredCategory.ObjectType:
            ...

class DeclaredCategory(_StaticRoles_DeclaredCategory, Category[[], [], _StaticRoles_DeclaredCategory.ObjectType, _StaticRoles_DeclaredCategory.ElementType, _StaticRoles_DeclaredCategory.MorphismType]):

    def __init__(self, name: str) -> None:
        ...

    def name(self) -> str:
        ...

class CategoryFamily:

    def __init__(self, name: str, domain: Category) -> None:
        ...

    def name(self) -> str:
        ...

    def domain(self) -> Category:
        ...

    def implemented_by(self, implementation: Functor) -> None:
        ...

    def __call__(self, argument: CategoryOfCategories.ElementType) -> Category:
        ...
Sets: Category
Posets: Category
Groupoids: Category
TotallyOrderedSets: Category
NN: Category
ZZ: Category
omega: Category
MagmaObjects: CategoryFamily
MonoidObjects: CategoryFamily
SemiringObjects: CategoryFamily
RingObjects: CategoryFamily
