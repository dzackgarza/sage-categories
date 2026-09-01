import sage_categories
from collections.abc import Hashable
from dataclasses import dataclass
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.predicates import Decision
__all__ = ['Datum', 'SetElementData', 'SetPointData', 'points_equal']
type Datum = Hashable

@dataclass(eq=False, slots=True)
class SetElementData:
    ...

@dataclass(eq=False, slots=True)
class SetPointData(SetElementData):
    datum: Datum

class SetElementDeclaration(sage_categories.kernel.roles.ElementOfObject):

    def __init__(self, data: SetElementData) -> None:
        ...

    def __hash__(self) -> int:
        ...

def points_equal(first: CategoryOfCategories.ElementType, candidate: CategoryOfCategories.ElementType) -> Decision:
    ...
