from sage_categories.cat.category import CategoryDeclaration as CategoryDeclaration
from sage_categories.cat.functors import FunctorDeclaration as FunctorDeclaration
from sage_categories.sets.category import Sets_Countable_ElementType as Sets_Countable_ElementType
from sage_categories.sets.category import Sets_Countable_MorphismType as Sets_Countable_MorphismType
from sage_categories.sets.category import Sets_Countable_ObjectType as Sets_Countable_ObjectType
from sage_categories.sets.elements import SetElementDeclaration as SetElementDeclaration
from sage_categories.sets.objects import SetObjectDeclaration as SetObjectDeclaration
from sage.rings.integer import Integer
from sage.rings.rational import Rational
from sage_categories.cat.category import Category as Category
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.kernel.decisions import Decision as Decision
from sage_categories.kernel.refinement import refine as refine
from sage_categories.kernel.roles import ElementOfObject as ElementOfObject, MorphismOfCategory as MorphismOfCategory, ObjectOfCategory as ObjectOfCategory
from sage_categories.sets.cardinals import aleph0 as aleph0
from sage_categories.sets.category import Sets as Sets
from sage_categories.sets.elements import Datum as Datum, SetElement as SetElement
from sage_categories.sets.maps import Rule as Rule
from sage_categories.sets.objects import SetObject as SetObject

class RationalSet(Sets_Countable_ObjectType):
    def __call__(self, rational: int | Integer | Rational) -> SetElement: ...

class RationalsCategory(CategoryDeclaration[[Rule], []]):
    @property
    def ObjectType(self) -> type[RationalSet]: ...
    @property
    def ElementType(self) -> type[RationalsCategory.DeclaredElementType]: ...
    @property
    def MorphismType(self) -> type[RationalsCategory.DeclaredMorphismType]: ...
    DeclaredObjectType = RationalSet
    class DeclaredElementType(Sets_Countable_ElementType):
        ...
    class DeclaredMorphismType(Sets_Countable_MorphismType):
        ...
    def __init__(self) -> None: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def __call__(self) -> SetObject: ...

def Rationals() -> RationalsCategory: ...

QQ: SetObject
