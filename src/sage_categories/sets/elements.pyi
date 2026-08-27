from collections.abc import Hashable
from dataclasses import dataclass
from sage_categories.kernel.decisions import Decision as Decision, Unknown as Unknown
from sage_categories.kernel.predicates import ask as ask
from sage_categories.kernel.roles import CategoryPoint as CategoryPoint, ElementOfObject as ElementOfObject, Role as Role, role_of as role_of
from typing import Any

type Datum = Hashable
@dataclass(eq=False, slots=True)
class SetElementData: ...

@dataclass(eq=False, slots=True)
class SetPointData(SetElementData):
    datum: Datum

class SetElementDeclaration(ElementOfObject):
    def __init__(self, data: SetElementData) -> None: ...
    def __hash__(self) -> int: ...

def points_equal(first: CategoryPoint, candidate: Any) -> Decision: ...
