from sage_categories.sets.category import Sets_Countable_ElementType as Sets_Countable_ElementType
from sage_categories.sets.category import Sets_Countable_MorphismType as Sets_Countable_MorphismType
from sage_categories.sets.category import Sets_Countable_ObjectType as Sets_Countable_ObjectType
from sage.rings.integer import Integer
from sage_categories.cat.category import Category as Category
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.kernel.decisions import Decision as Decision, Unknown as Unknown
from sage_categories.kernel.predicates import Predicate as Predicate
from sage_categories.kernel.roles import CategoryPoint as CategoryPoint, ElementOfObject as ElementOfObject, MorphismOfCategory as MorphismOfCategory, ObjectOfCategory as ObjectOfCategory
from sage_categories.sets.cardinals import aleph0 as aleph0
from sage_categories.sets.category import Sets as Sets
from sage_categories.sets.elements import Datum as Datum, SetPoint as SetPoint
from sage_categories.sets.maps import Rule as Rule
from sage_categories.sets.objects import SetObject as SetObject

class PositiveIntegerSet(Sets_Countable_ObjectType):
    def __call__(self, integer: int | Integer) -> SetPoint: ...

class PositiveIntegersCategory(Category[[Rule], []]):
    @property
    def ObjectType(self) -> type[PositiveIntegerSet]: ...
    class ElementType(Sets_Countable_ElementType):
        ...
    class MorphismType(Sets_Countable_MorphismType):
        ...
    def __init__(self) -> None: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def __call__(self) -> SetObject: ...

natural_order: Predicate

def PositiveIntegers() -> PositiveIntegersCategory: ...

NN: SetObject
