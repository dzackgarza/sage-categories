import sage_categories
from collections.abc import Callable
from dataclasses import dataclass
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.predicates import Decision
from sage_categories.sets.category import SetElement, SetObject
from sage_categories.sets.elements import Datum
__all__ = ['Rule', 'SetMorphismData', 'maps_equal', 'injective_on_finite_domain', 'surjective_on_finite_domain']
type Rule = Callable[[Datum], Datum]

@dataclass(eq=False, slots=True)
class SetMorphismData:
    rule: Rule

class SetMapDeclaration(sage_categories.kernel.roles.MorphismOfCategory):

    def __init__(self, data: SetMorphismData) -> None:
        ...

    def __call__(self, element: SetElement) -> SetElement:
        ...

    def image(self) -> SetObject:
        ...

def maps_equal(first: CategoryOfCategories.ElementType, candidate: CategoryOfCategories.ElementType, assumptions: Proposition) -> Decision:
    ...

def injective_on_finite_domain(morphism: SetMapDeclaration, assumptions: Proposition) -> Decision:
    ...

def surjective_on_finite_domain(morphism: SetMapDeclaration, assumptions: Proposition) -> Decision:
    ...
