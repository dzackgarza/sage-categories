"""``Sets().ElementType``: generalized elements ``T -> X`` (POL-CAT-058, POL-FUN-002).

A classical element of a set ``X`` is a generalized element whose stage is the
classical stage ``Sets().Terminal()``: a point ``1 -> X``.  It retains its defining
morphism and, at the private computation boundary, the datum that the point
selects.  A generalized element at another stage retains no point datum.  Two
classical points of one set are equal exactly when their data are equal; a point
hashes by its datum, so equal points hash equal.
"""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import sage_categories.sets.category as _sets
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import ask
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, Role, role_of

if TYPE_CHECKING:
    from sage_categories.sets.category import SetElement

__all__ = ["Datum", "SetElementData", "SetPointData", "points_equal"]

type Datum = Hashable


@dataclass(eq=False, slots=True)
class SetElementData:
    """The private state used by the complete set-element implementation."""

    canonical: SetElement = field(init=False)

    def bind(self, canonical: SetElement) -> None:
        """Bind direct construction once; inherited construction reuses that state."""
        if not hasattr(self, "canonical"):
            self.canonical = canonical


@dataclass(eq=False, slots=True)
class SetPointData(SetElementData):
    """The additional chosen datum of a terminal-stage set element."""

    datum: Datum


class SetElementDeclaration(ElementOfObject):
    """The local ``Sets().ElementType`` declaration."""

    def __init__(self, data: SetElementData) -> None:
        data.bind(self)
        self._set_element_data = data
        super().__init__()

    def __hash__(self) -> int:
        if isinstance(self._set_element_data, SetPointData):
            return hash(self._set_element_data.datum)
        return super().__hash__()

    def __repr__(self) -> str:
        if isinstance(self._set_element_data, SetPointData):
            return f"{self._set_element_data.datum!r} in {self.parent()!r}"
        return f"{self.defining_morphism()!r} as a generalized element of {self.parent()!r}"

    def _point_datum_(self) -> Datum:
        """The selected datum of this terminal-stage element."""
        assert self.defining_morphism().domain() is _sets.Sets().Terminal(), f"{self!r} is not a classical set element"
        return self._set_element_data.datum


def points_equal(first: CategoryPoint, candidate: Any) -> Decision:
    """Two classical points of one set are equal exactly when their data are.

    A generalized element is classical exactly when its stage is the classical stage of
    ``Sets()`` (POL-CAT-058); at any other stage this handler decides nothing.  The two
    data compare at the private boundary, where ``==`` is exact for an engine value,
    ``Unknown`` for a rule-defined family, and a proposition for an owned mathematical
    value, so the comparison is asked rather than returned (POL-MATH-034).
    """
    if role_of(first) is not Role.ELEMENT or role_of(candidate) is not Role.ELEMENT:
        return Unknown
    if first.parent() is not candidate.parent():
        return Unknown
    classical = _sets.Sets().Terminal()
    if first.defining_morphism().domain() is not classical or candidate.defining_morphism().domain() is not classical:
        return Unknown
    return ask(first._point_datum_() == candidate._point_datum_())
