"""Rule-defined set objects and their local set operations."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from sage.structure.coerce_dict import MonoDict

import sage_categories.sets.category as _sets
from sage_categories.cat.predicates import (
    AppliedPredicate,
    Decision,
    Predicate,
    Proposition,
    Unknown,
    UnknownClass,
    ask,
    conjunction,
    disjunction,
    predicate,
)
from sage_categories.kernel.roles import Role, role_of
from sage_categories.sets.elements import Datum, SetPointData

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.sets.cardinals import CardinalObject
    from sage_categories.sets.category import SetElement, SetMap, SetObject

__all__ = ["MembershipRule", "SetObjectData", "element_of", "sets_equal"]


type MembershipRule = Callable[[Datum], Decision]

# ``element_of(x, X)``: the point ``x`` lies in the set ``X``.
element_of: Predicate = predicate("element_of")


def _element_of(
    candidate: CategoryOfCategories.ElementType, ambient: SetObjectDeclaration, assumptions: Proposition
) -> Decision:
    """The one exact ``element_of`` case on a set: parenthood first, then the membership rule.

    A point ``* -> X`` is an element of ``X`` by definition (POL-CAT-058), so
    parenthood decides before any rule runs.  Otherwise the membership rule decides
    a point from its stored datum: a non-element candidate gives ``False``, and a
    generalized element with nonterminal domain retains no point datum, so the
    decision there is ``Unknown``.
    """
    if role_of(candidate) is not Role.ELEMENT:
        return False
    if candidate.parent() is ambient:
        return True
    state = candidate._set_element_data
    if not isinstance(state, SetPointData):
        return Unknown
    return ambient._set_object_data.membership_rule(state.datum)


def sets_equal(
    first: SetObjectDeclaration, candidate: SetObjectDeclaration, assumptions: Proposition
) -> Decision:
    """Two sets with chosen enumerations are equal exactly when they have the same members.

    This is extensionality (Mathlib ``Set.ext_iff``, ``Mathlib/Data/Set/Defs.lean``:
    ``a = b ↔ ∀ (x : α), x ∈ a ↔ x ∈ b``; inspected 2026-08-28).  The enumeration
    constructor asserts that an enumeration lists exactly distinct data, so two
    enumerations of one length list the same members exactly when every member of the
    first is a member of the second.  Without a chosen enumeration on both sides the
    members are not available and the handler decides nothing.
    """
    finite = _sets.Sets().Finite()
    if not first._is_object() or role_of(candidate) is not Role.OBJECT:
        return Unknown
    if not finite.has_chosen_enumeration(first) or not finite.has_chosen_enumeration(
        candidate
    ):
        return Unknown
    left, right = finite.chosen_enumeration(first), finite.chosen_enumeration(candidate)
    if len(left) != len(right):
        return False
    return ask(
        conjunction(disjunction(member == other for other in right) for member in left)
    )


@dataclass(eq=False, slots=True)
class SetObjectData:
    """The private state used by the complete set-object implementation."""

    membership_rule: MembershipRule
    cardinality: CardinalObject | UnknownClass
    cardinality_evaluator: Callable[[], CardinalObject | UnknownClass] | None = None
    points: dict[Datum, SetElement] = field(default_factory=dict)
    rule_points: MonoDict = field(default_factory=MonoDict)


class SetObjectDeclaration:
    """The local ``Sets().ObjectType`` declaration."""

    def __init__(self, data: SetObjectData) -> None:
        self._set_object_data = data
        super().__init__()

    def membership_proposition(
        self, candidate: CategoryOfCategories.ElementType
    ) -> AppliedPredicate:
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
        """The point ``* -> X`` selecting ``datum``, one point per datum value.

        A set constructed through ``Sets().rule_valued`` routes every point through
        ``rule_point``, since its data compare three-valued.
        """
        state = self._set_object_data
        if _sets.Sets().points_by_rule(self):
            return self.rule_point(datum)
        assert state.membership_rule(datum) is not False, (
            f"{datum!r} is not a member of {self!r}"
        )
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
        assert state.membership_rule(datum) is not False, (
            f"{datum!r} is not a member of {self!r}"
        )
        if datum not in state.rule_points:
            state.rule_points[datum] = self._construct_point(datum)
        return state.rule_points[datum]

    def _construct_point(self, datum: Datum) -> SetElement:
        sets = _sets.Sets()
        return sets.element_from_defining_morphism(
            sets.construct_morphism(sets.Terminal(), self, lambda star: datum)
        )

    def cardinality(self) -> AppliedQuery:
        """Return the applied cardinality query with result category Cardinal()."""
        from sage_categories.sets.cardinals import cardinality_query

        return cardinality_query(self)

    def subset_from(self, predicate: MembershipRule) -> SetObject:
        """The chosen subset ``{x in X : predicate(x)}`` with its subcategory monomorphism (POL-SET-007, POL-ENGINE-004).

        The predicate is a datum-level rule, the form of ``Sets()(rule)``; the
        construction is owned by ``Sets().ChosenSubsets()`` (``sets/subobjects.py``).
        """
        return _sets.Sets().ChosenSubsets()(self, predicate)

    def is_empty(self) -> AppliedPredicate:
        return _sets.Sets()._empty.predicate()(self)

    def is_inhabited(self) -> AppliedPredicate:
        return _sets.Sets().Inhabited().predicate()(self)

    def is_finite(self) -> AppliedPredicate:
        return _sets.Sets().Finite().predicate()(self)

    def is_infinite(self) -> AppliedPredicate:
        return _sets.Sets().Infinite().predicate()(self)

    def is_countable(self) -> AppliedPredicate:
        return _sets.Sets().Countable().predicate()(self)

    def is_uncountable(self) -> AppliedPredicate:
        return _sets.Sets().Uncountable().predicate()(self)

    def evaluation_isomorphism(self) -> SetMap:
        r"""The evaluation isomorphism ``\coprod_{x \in X} 1 \cong X`` (specs/separating-families-and-categorical-generators.md)."""
        sets = _sets.Sets()
        finite = sets.Finite()
        if finite.has_chosen_enumeration(self):
            enumeration = finite.chosen_enumeration(self)
            coprod = finite.from_enumeration((datum, ()) for datum in enumeration)
        else:
            coprod = sets(lambda datum: (
                isinstance(datum, tuple)
                and len(datum) == 2
                and datum[1] == ()
                and self._set_object_data.membership_rule(datum[0]) is not False
            ))
        return sets.construct_morphism(
            coprod,
            self,
            lambda tagged: tagged[0],
            lambda datum: (datum, ()),
        )

    def __repr__(self) -> str:
        finite = _sets.Sets().Finite()
        if finite.has_chosen_enumeration(self):
            return "{" + ", ".join(map(repr, finite.chosen_enumeration(self))) + "}"
        return "Set(<rule>)"


element_of.register_handler(_element_of)


def set_cardinality(set_obj: SetObjectDeclaration) -> CardinalObject | UnknownClass:
    """The recorded exact cardinal; a set placed in both ``Countable()`` and ``Infinite()`` has ``aleph0`` (Mathlib ``Cardinal.mk_eq_aleph0``; inspected 2026-08-27)."""
    state = set_obj._set_object_data
    if state.cardinality is not Unknown:
        return state.cardinality
    if state.cardinality_evaluator is not None:
        evaluated = state.cardinality_evaluator()
        if evaluated is not Unknown:
            return evaluated
    finite = _sets.Sets().Finite()
    if finite.has_chosen_enumeration(set_obj):
        from sage_categories.sets.cardinals import Cardinal

        return Cardinal()(len(finite.chosen_enumeration(set_obj)))
    sets = _sets.Sets()
    from sage_categories.kernel.refinement import is_placed

    if is_placed(set_obj, sets.Countable()) and is_placed(set_obj, sets.Infinite()):
        from sage_categories.sets.cardinals import Cardinal

        return Cardinal().aleph(0)
    return Unknown


class FiniteSetObject:
    """The local object role of ``Sets().Finite()``: the chosen enumeration supplies iteration."""

    def __iter__(self) -> Iterator[SetElement]:
        return (
            self.point(datum)
            for datum in _sets.Sets().Finite().chosen_enumeration(self)
        )
