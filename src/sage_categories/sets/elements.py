"""``Sets().ElementType``: classical elements as points ``1 -> X`` (POL-CAT-058, POL-SET-026).

A classical element of a set ``X`` is a generalized element whose stage is the
classical stage ``Sets().Terminal()``: a point ``1 -> X``.  It retains its defining
morphism and, at the private computation boundary, the datum that the point
selects.  Two points of one set are equal exactly when their data are equal; a
point hashes by its datum, so equal points hash equal.
"""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, Role, role_of

if TYPE_CHECKING:
    from sage_categories.kernel.roles import MorphismOfCategory

__all__ = ["Datum", "SetElementData", "SetPoint", "points_equal"]

type Datum = Hashable


@dataclass(eq=False, slots=True)
class SetElementData:
    """The private state used by the complete set-element implementation."""

    datum: Datum
    canonical: SetPoint = field(init=False)

    def bind(self, canonical: SetPoint) -> None:
        """Bind direct construction once; inherited construction reuses that state."""
        if not hasattr(self, "canonical"):
            self.canonical = canonical


class SetPoint(ElementOfObject):
    """A point ``1 -> X`` of a set, selecting the private datum ``datum``."""

    def __init__(self, data: SetElementData) -> None:
        data.bind(self)
        self._set_element_data = data
        super().__init__()

    def __hash__(self) -> int:
        return hash(self._set_element_data.datum)

    def __repr__(self) -> str:
        return f"{self._set_element_data.datum!r} in {self.parent()!r}"


def points_equal(first: CategoryPoint, candidate: Any) -> Decision:
    """Two points of one set are equal exactly when their data are (the engine comparison is exact)."""
    if role_of(first) is not Role.ELEMENT or role_of(candidate) is not Role.ELEMENT:
        return Unknown
    if first.parent() is not candidate.parent():
        return Unknown
    return first._set_element_data.datum == candidate._set_element_data.datum
