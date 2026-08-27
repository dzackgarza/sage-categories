from collections.abc import Hashable
from sage_categories.kernel.decisions import Decision as Decision, Unknown as Unknown
from sage_categories.kernel.roles import CategoryPoint as CategoryPoint, ElementOfObject as ElementOfObject, MorphismOfCategory as MorphismOfCategory, Role as Role, role_of as role_of
from typing import Any

type Datum = Hashable
class SetPoint(ElementOfObject):
    def __init__(self, defining_morphism: MorphismOfCategory, datum: Datum) -> None: ...
    def __hash__(self) -> int: ...

def points_equal(first: CategoryPoint, candidate: Any) -> Decision: ...
