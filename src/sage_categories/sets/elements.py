"""``Sets().ElementType``: generalized elements ``T -> X``.

A point of a set ``X`` has terminal domain and is written ``* -> X``.
Only such points retain a chosen datum.
Two points of one set compare and hash by that datum.
"""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import sage_categories.sets.category as _sets
from sage_categories.cat.predicates import Decision, Unknown
from sage_categories.cat.predicates import ask

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

__all__ = ["Datum", "SetElementData", "SetPointData", "points_equal"]

type Datum = Hashable


@dataclass(eq=False, slots=True)
class SetElementData:
    """The private state used by the complete set-element implementation."""


@dataclass(eq=False, slots=True)
class SetPointData(SetElementData):
    """The additional chosen datum of a point of a set."""

    datum: Datum


class SetElementDeclaration:
    """The local ``Sets().ElementType`` declaration."""

    def __init__(self, data: SetElementData) -> None:
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
        """The selected datum of this point."""
        assert self.defining_morphism().domain() is _sets.Sets().Terminal(), f"{self!r} is not a point of a set"
        return self._set_element_data.datum


def points_equal(first: CategoryOfCategories.ElementType, candidate: Any) -> Decision:
    """Two points of one set are equal exactly when their data are.

    A generalized element is a point exactly when its domain is the terminal object of
    ``Sets()`` (POL-CAT-058); with any other domain this handler decides nothing.  The two
    data compare at the private boundary, where ``==`` is exact for an engine value,
    ``Unknown`` for a rule-defined family, and a proposition for an owned mathematical
    value, so the comparison is asked rather than returned (POL-MATH-034).
    """
    if not first._is_element() or not hasattr(candidate, "_is_element") or not candidate._is_element():
        return Unknown
    if first.parent() is not candidate.parent():
        return Unknown
    terminal = _sets.Sets().Terminal()
    if first.defining_morphism().domain() is not terminal or candidate.defining_morphism().domain() is not terminal:
        return Unknown
    return ask(first._point_datum_() == candidate._point_datum_())
