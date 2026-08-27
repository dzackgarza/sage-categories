"""``Sets().ObjectType``: rule-defined sets (POL-ASSUME-004, POL-SET-016, POL-SET-026).

A set is defined by a membership rule on private data; it needs no enumeration
(POL-SET-016/029).  ``X.membership_proposition(x)`` is the applied ``element_of``
predicate whose exact handler calls the rule; ``x in X`` is the Boolean boundary.
``X.cardinality()`` returns an exact cardinal or Sage ``Unknown``; the cardinal
property methods return applied predicates decided by category placement, active
assumptions, the implications ``Finite => Countable`` and
``Uncountable => Infinite``, and the exact route "a known cardinality decides
finiteness and countability" (``specs/sets.md``, "Cardinality and enumeration").

A chosen enumeration is structure a finite set has, not a field of every set: it is
retained by ``Sets().Finite()``, whose enumeration constructor records it
(``specs/sets.md``, "Cardinality and enumeration").  Iteration reads it there.
Likewise ``X.subset_from(predicate)`` constructs through ``Sets().ChosenSubsets()``,
which retains each inclusion (``sets/subobjects.py``).
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any

from sage.structure.coerce_dict import MonoDict

import sage_categories.sets.category as _sets
from sage_categories.cat.category import Category
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import AppliedPredicate, Predicate, ask
from sage_categories.kernel.roles import CategoryPoint, ObjectOfCategory, Role, role_of
from sage_categories.sets.cardinals import Cardinal, CardinalObject
from sage_categories.sets.elements import Datum, SetPoint

__all__ = ["FiniteSetRole", "MembershipRule", "SetObject", "SetObjectData", "element_of"]

logger = logging.getLogger("sage_categories")

type MembershipRule = Callable[[Datum], Decision]

# ``element_of(x, X)``: the point ``x`` lies in the set ``X``.
element_of = Predicate("element_of", 2, True)


def _element_of_by_parent(candidate: Any, ambient: SetObject) -> Decision:
    """A point ``1 -> X`` is an element of ``X`` by definition (POL-CAT-058)."""
    if role_of(candidate) is Role.ELEMENT and candidate.parent() is ambient:
        return True
    return Unknown


def _element_of_by_rule(candidate: Any, ambient: SetObject) -> Decision:
    if role_of(candidate) is not Role.ELEMENT:
        return False
    return ambient._set_object_data.membership_rule(candidate._set_element_data.datum)


element_of.register_handler(_element_of_by_parent)
element_of.register_handler(_element_of_by_rule)


@dataclass(eq=False, slots=True)
class SetObjectData:
    """The private state used by the complete set-object implementation."""

    membership_rule: MembershipRule
    cardinality: CardinalObject | UnknownClass
    points: dict[Datum, SetPoint] = field(default_factory=dict)
    rule_points: MonoDict = field(default_factory=MonoDict)
    canonical: SetObject = field(init=False)

    def bind(self, canonical: SetObject) -> None:
        """Bind direct construction once; inherited construction reuses that state."""
        if not hasattr(self, "canonical"):
            self.canonical = canonical


class SetObject(ObjectOfCategory):
    """A set given by a membership rule, with its cardinal data when known."""

    def __init__(self, data: SetObjectData) -> None:
        data.bind(self)
        self._set_object_data = data
        super().__init__()

    def membership_proposition(self, candidate: CategoryPoint) -> AppliedPredicate:
        return element_of(candidate, self)

    def __contains__(self, candidate: Any) -> bool:
        decision = ask(element_of(candidate, self))
        if decision is Unknown:
            logger.info("membership of %r in %r was not established", candidate, self)
            return False
        return decision is True

    def point(self, datum: Datum) -> SetPoint:
        """The classical element ``1 -> X`` selecting ``datum``, one point per datum value.

        A set constructed through ``Sets().rule_valued`` routes every point through
        ``rule_point``, since its data compare three-valued.
        """
        state = self._set_object_data
        if _sets.Sets().points_by_rule(state.canonical):
            return self.rule_point(datum)
        assert state.membership_rule(datum) is not False, f"{datum!r} is not a member of {self!r}"
        if datum not in state.points:
            state.points[datum] = self._construct_point(datum)
        return state.points[datum]

    def rule_point(self, datum: Datum) -> SetPoint:
        """The point selecting a rule datum, one point per datum object.

        Two distinct-but-equal rule data yield two points that are ``True``-equal
        (their data compare equal through the engine) and hash-equal (a point hashes
        by its datum, and equal rule data hash equal).
        """
        state = self._set_object_data
        assert state.membership_rule(datum) is not False, f"{datum!r} is not a member of {self!r}"
        if datum not in state.rule_points:
            state.rule_points[datum] = self._construct_point(datum)
        return state.rule_points[datum]

    def _construct_point(self, datum: Datum) -> SetPoint:
        sets = _sets.Sets()
        canonical = self._set_object_data.canonical
        return sets.element_from_defining_morphism(sets.construct_morphism(sets.Terminal(), canonical, lambda star: datum))

    def cardinality(self) -> CardinalObject | UnknownClass:
        """The recorded exact cardinal; a set placed in both ``Countable()`` and ``Infinite()`` has ``aleph0`` (Mathlib ``Cardinal.mk_eq_aleph0``; inspected 2026-08-27)."""
        sets = _sets.Sets()
        state = self._set_object_data
        if state.cardinality is Unknown and state.canonical in sets.Countable() and state.canonical in sets.Infinite():
            return Cardinal().aleph(0)
        return state.cardinality

    def subset_from(self, predicate: MembershipRule) -> SetObject:
        """The chosen subset ``{x in X : predicate(x)}`` with its retained inclusion (POL-SET-007, POL-ENGINE-004).

        The predicate is a datum-level rule, the form of ``Sets()(rule)``; the
        construction is owned by ``Sets().ChosenSubsets()`` (``sets/subobjects.py``).
        """
        return _sets.Sets().ChosenSubsets()(self._set_object_data.canonical, predicate)

    def is_finite(self) -> AppliedPredicate:
        return _sets.Sets().Finite().predicate()(self._set_object_data.canonical)

    def is_infinite(self) -> AppliedPredicate:
        return _sets.Sets().Infinite().predicate()(self._set_object_data.canonical)

    def is_countable(self) -> AppliedPredicate:
        return _sets.Sets().Countable().predicate()(self._set_object_data.canonical)

    def is_uncountable(self) -> AppliedPredicate:
        return _sets.Sets().Uncountable().predicate()(self._set_object_data.canonical)

    def __repr__(self) -> str:
        finite = _sets.Sets().Finite()
        canonical = self._set_object_data.canonical
        if finite.has_chosen_enumeration(canonical):
            return "{" + ", ".join(map(repr, finite.chosen_enumeration(canonical))) + "}"
        return "Set(<rule>)"


class FiniteSetRole(ObjectOfCategory):
    """The local object role of ``Sets().Finite()``: the chosen enumeration supplies iteration."""

    def __iter__(self) -> Iterator[SetPoint]:
        canonical = self._set_object_data.canonical
        return (self.point(datum) for datum in _sets.Sets().Finite().chosen_enumeration(canonical))
