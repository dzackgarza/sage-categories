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
which retains each presenting monomorphism (``sets/subobjects.py``).
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from sage.structure.coerce_dict import MonoDict

import sage_categories.sets.category as _sets
from sage_categories.cat.category import Category
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import AppliedPredicate, Predicate, ask, conjunction, disjunction
from sage_categories.kernel.roles import CategoryPoint, ObjectOfCategory, Role, role_of
from sage_categories.sets.elements import Datum, SetPointData

if TYPE_CHECKING:
    from sage_categories.sets.cardinals import CardinalObject
    from sage_categories.sets.category import SetElement, SetObject

__all__ = ["MembershipRule", "SetObjectData", "element_of", "sets_equal"]


type MembershipRule = Callable[[Datum], Decision]

# ``element_of(x, X)``: the point ``x`` lies in the set ``X``.
element_of: Predicate = Predicate("element_of", 2, True)


def _element_of_by_parent(candidate: Any, ambient: SetObject) -> Decision:
    """A point ``1 -> X`` is an element of ``X`` by definition (POL-CAT-058)."""
    if role_of(candidate) is Role.ELEMENT and candidate.parent() is ambient:
        return True
    return Unknown


def _element_of_by_rule(candidate: Any, ambient: SetObject) -> Decision:
    """The membership rule decides a point of ``ambient`` on its datum; a candidate that is no element is none.

    ``element_of(x, X)`` is the proposition "the point ``x`` lies in the set ``X``",
    and an element of ``X`` is a morphism ``1 -> X``: "set membership, enumeration,
    and cardinality use ``Mor(Sets())(1, X)`` through this separator"
    (``specs/sets.md``, "Canonical objects").  So a raw datum is not an element of any
    set, and ``False`` is that proposition's value rather than a missing decision:
    ``2`` and ``X.point(2)`` are two values, and no algorithm turns the first into the
    second.  This is the shape of ``is_placed`` (``kernel/refinement.py``), which
    ``POL-TYPE-004`` authorizes for the same ``Any`` candidate position.  A datum's
    own question is ``X.point(datum) in X``.

    A generalized element at another stage carries no datum, so the rule cannot reach
    it and the decision is ``Unknown``.
    """
    if role_of(candidate) is not Role.ELEMENT:
        return False
    state = candidate._set_element_data
    if not isinstance(state, SetPointData):
        return Unknown
    return ambient._set_object_data.membership_rule(state.datum)


element_of.register_handler(_element_of_by_parent)
element_of.register_handler(_element_of_by_rule)


def sets_equal(first: CategoryPoint, candidate: Any) -> Decision:
    """Two sets with chosen enumerations are equal exactly when they have the same members.

    This is extensionality (Mathlib ``Set.ext_iff``, ``Mathlib/Data/Set/Defs.lean``:
    ``a = b ↔ ∀ (x : α), x ∈ a ↔ x ∈ b``; inspected 2026-08-28).  The enumeration
    constructor asserts that an enumeration lists exactly distinct data, so two
    enumerations of one length list the same members exactly when every member of the
    first is a member of the second.  Without a chosen enumeration on both sides the
    members are not available and the handler decides nothing.
    """
    finite = _sets.Sets().Finite()
    if role_of(first) is not Role.OBJECT or role_of(candidate) is not Role.OBJECT:
        return Unknown
    if not finite.has_chosen_enumeration(first) or not finite.has_chosen_enumeration(candidate):
        return Unknown
    left, right = finite.chosen_enumeration(first), finite.chosen_enumeration(candidate)
    if len(left) != len(right):
        return False
    return ask(conjunction(disjunction(member == other for other in right) for member in left))


@dataclass(eq=False, slots=True)
class SetObjectData:
    """The private state used by the complete set-object implementation."""

    membership_rule: MembershipRule
    cardinality: CardinalObject | UnknownClass
    points: dict[Datum, SetElement] = field(default_factory=dict)
    rule_points: MonoDict = field(default_factory=MonoDict)


class SetObjectDeclaration(ObjectOfCategory):
    """The local ``Sets().ObjectType`` declaration."""

    def __init__(self, data: SetObjectData) -> None:
        self._set_object_data = data
        super().__init__()

    def membership_proposition(self, candidate: CategoryPoint) -> AppliedPredicate:
        return element_of(candidate, self)

    def __contains__(self, candidate: Any) -> bool:
        """``x in X``, for a set whose membership the available data decide.

        Membership in a set is a mathematical predicate and can be undecided, while
        ``__contains__`` must return a bool, so an undecided membership fails loudly
        here rather than being reported as non-membership: ``Unknown`` is not ``False``.
        The three-valued question is ``ask(X.membership_proposition(x))``, which every
        caller that must handle the undecided case asks instead.
        """
        decision = ask(element_of(candidate, self))
        assert decision is not Unknown, (
            f"membership of {candidate!r} in {self!r} is not established by the available data and algorithms; "
            f"ask(this_set.membership_proposition(candidate)) for the three-valued answer"
        )
        return bool(decision)

    def point(self, datum: Datum) -> SetElement:
        """The point ``1 -> X`` selecting ``datum``, one point per datum value.

        A set constructed through ``Sets().rule_valued`` routes every point through
        ``rule_point``, since its data compare three-valued.
        """
        state = self._set_object_data
        if _sets.Sets().points_by_rule(_sets.Sets().structural_image(self)):
            return self.rule_point(datum)
        assert state.membership_rule(datum) is not False, f"{datum!r} is not a member of {self!r}"
        if datum not in state.points:
            state.points[datum] = self._construct_point(datum)
        return state.points[datum]

    def rule_point(self, datum: Datum) -> SetElement:
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

    def _construct_point(self, datum: Datum) -> SetElement:
        sets = _sets.Sets()
        underlying = sets.structural_image(self)
        return sets.element_from_defining_morphism(sets.construct_morphism(sets.Terminal(), underlying, lambda star: datum))

    def cardinality(self) -> CardinalObject | UnknownClass:
        """The recorded exact cardinal; a set placed in both ``Countable()`` and ``Infinite()`` has ``aleph0`` (Mathlib ``Cardinal.mk_eq_aleph0``; inspected 2026-08-27)."""
        from sage_categories.sets.cardinals import Cardinal

        sets = _sets.Sets()
        state = self._set_object_data
        underlying = sets.structural_image(self)
        if state.cardinality is Unknown and underlying in sets.Countable() and underlying in sets.Infinite():
            return Cardinal().aleph(0)
        return state.cardinality

    def subset_from(self, predicate: MembershipRule) -> SetObject:
        """The chosen subset ``{x in X : predicate(x)}`` with its subcategory monomorphism (POL-SET-007, POL-ENGINE-004).

        The predicate is a datum-level rule, the form of ``Sets()(rule)``; the
        construction is owned by ``Sets().ChosenSubsets()`` (``sets/subobjects.py``).
        """
        return _sets.Sets().ChosenSubsets()(_sets.Sets().structural_image(self), predicate)

    def is_finite(self) -> AppliedPredicate:
        return _sets.Sets().Finite().predicate()(_sets.Sets().structural_image(self))

    def is_infinite(self) -> AppliedPredicate:
        return _sets.Sets().Infinite().predicate()(_sets.Sets().structural_image(self))

    def is_countable(self) -> AppliedPredicate:
        return _sets.Sets().Countable().predicate()(_sets.Sets().structural_image(self))

    def is_uncountable(self) -> AppliedPredicate:
        return _sets.Sets().Uncountable().predicate()(_sets.Sets().structural_image(self))

    def __repr__(self) -> str:
        finite = _sets.Sets().Finite()
        underlying = _sets.Sets().structural_image(self)
        if finite.has_chosen_enumeration(underlying):
            return "{" + ", ".join(map(repr, finite.chosen_enumeration(underlying))) + "}"
        return "Set(<rule>)"


class FiniteSetRole(ObjectOfCategory):
    """The local object role of ``Sets().Finite()``: the chosen enumeration supplies iteration."""

    def __iter__(self) -> Iterator[SetElement]:
        underlying = _sets.Sets().structural_image(self)
        return (self.point(datum) for datum in _sets.Sets().Finite().chosen_enumeration(underlying))
