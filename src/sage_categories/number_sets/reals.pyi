from sage_categories.cat.category import CategoryDeclaration as CategoryDeclaration
from sage_categories.cat.functors import FunctorDeclaration as FunctorDeclaration
from sage_categories.sets.category import Sets_Uncountable_ElementType as Sets_Uncountable_ElementType
from sage_categories.sets.category import Sets_Uncountable_MorphismType as Sets_Uncountable_MorphismType
from sage_categories.sets.category import Sets_Uncountable_ObjectType as Sets_Uncountable_ObjectType
from sage_categories.sets.elements import SetElementDeclaration as SetElementDeclaration
from sage_categories.sets.objects import SetObjectDeclaration as SetObjectDeclaration
from sage.rings.integer import Integer
from sage.rings.qqbar import AlgebraicReal
from sage.rings.rational import Rational
from sage_categories.cat.category import Category as Category
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.kernel.decisions import Decision as Decision, Unknown as Unknown
from sage_categories.kernel.refinement import refine as refine
from sage_categories.kernel.roles import ElementOfObject as ElementOfObject, MorphismOfCategory as MorphismOfCategory, ObjectOfCategory as ObjectOfCategory
from sage_categories.sets.cardinals import continuum as continuum
from sage_categories.sets.category import Sets as Sets
from sage_categories.sets.elements import Datum as Datum, SetElement as SetElement
from sage_categories.sets.maps import Rule as Rule
from sage_categories.sets.objects import SetObject as SetObject

class RealSet(Sets_Uncountable_ObjectType):
    def __call__(self, real: int | Integer | Rational | AlgebraicReal) -> SetElement: ...

class RealsCategory(CategoryDeclaration[[Rule], []]):
    @property
    def ObjectType(self) -> type[RealSet]: ...
    @property
    def ElementType(self) -> type[RealsCategory.DeclaredElementType]: ...
    @property
    def MorphismType(self) -> type[RealsCategory.DeclaredMorphismType]: ...
    DeclaredObjectType = RealSet
    class DeclaredElementType(Sets_Uncountable_ElementType):
        ...
    class DeclaredMorphismType(Sets_Uncountable_MorphismType):
        ...
    def __init__(self) -> None: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def __call__(self) -> SetObject: ...

def Reals() -> RealsCategory: ...

RR: SetObject
