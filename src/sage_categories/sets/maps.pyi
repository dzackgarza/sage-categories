from sage_categories.cat.category import CategoryDeclaration as CategoryDeclaration
from sage_categories.cat.elements import CategoryPointDeclaration as CategoryPointDeclaration
from sage_categories.sets.elements import SetElementDeclaration as SetElementDeclaration
from sage_categories.sets.objects import SetObjectDeclaration as SetObjectDeclaration
from collections.abc import Callable
from dataclasses import dataclass, field
from sage_categories.cat.category import Category as Category
from sage_categories.kernel.decisions import Decision as Decision, Unknown as Unknown, decision_and as decision_and, decision_not as decision_not, decision_or as decision_or
from sage_categories.kernel.roles import CategoryPoint as CategoryPoint, MorphismOfCategory as MorphismOfCategory
from sage_categories.sets.category import SetElement as SetElement, SetMap as SetMap, SetObject as SetObject
from sage_categories.sets.elements import Datum as Datum, data_equal as data_equal
from typing import Any

type Rule = Callable[[Datum], Datum]
@dataclass(eq=False, slots=True)
class SetMorphismData:
    rule: Rule
    canonical: SetMap = field(init=False)
    def bind(self, canonical: SetMap) -> None: ...

class SetMapDeclaration(MorphismOfCategory):
    def __init__(self, data: SetMorphismData) -> None: ...
    def __call__(self, element: SetElement) -> SetElement: ...
    def image(self) -> SetObject: ...

def maps_equal(first: CategoryPoint, candidate: Any) -> Decision: ...
def injective_on_finite_domain(morphism: MorphismOfCategory) -> Decision: ...
def surjective_on_finite_domain(morphism: MorphismOfCategory) -> Decision: ...
def bijective_on_finite_domain(morphism: MorphismOfCategory) -> Decision: ...
