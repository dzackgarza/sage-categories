"""``Sets().ObjectType``: rule-defined sets (D01, D11, D17).

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
from typing import Any

from sage.structure.coerce_dict import MonoDict

import sage_categories.sets.category as _sets
from sage_categories.cat.category import Category
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import AppliedPredicate, Predicate, ask
from sage_categories.kernel.roles import CategoryPoint, ObjectOfCategory, Role, role_of
from sage_categories.sets.cardinals import Cardinal, CardinalObject
from sage_categories.sets.elements import Datum, SetPoint

__all__ = ["FiniteSetRole", "MembershipRule", "SetObject", "element_of"]

logger = logging.getLogger("sage_categories")

type MembershipRule = Callable[[Datum], Decision]

# ``element_of(x, X)``: the point ``x`` lies in the set ``X``.
element_of = Predicate("element_of", 2, True)


def _element_of_by_parent(candidate: Any, ambient: SetObject) -> Decision:
    """A point ``1 -> X`` is an element of ``X`` by definition (D06)."""
    if role_of(candidate) is Role.ELEMENT and candidate.parent() is ambient:
        return True
    return Unknown


def _element_of_by_rule(candidate: Any, ambient: SetObject) -> Decision:
    if role_of(candidate) is not Role.ELEMENT:
        return False
    return ambient._membership_rule(candidate._datum)


element_of.register_handler(_element_of_by_parent)
element_of.register_handler(_element_of_by_rule)


class SetObject(ObjectOfCategory):
    """A set given by a membership rule, with its cardinal data when known."""

    def __init__(
        self,
        category: Category,
        membership_rule: MembershipRule,
        cardinality: CardinalObject | UnknownClass,
    ) -> None:
        super().__init__(category)
        self._membership_rule = membership_rule
        self._cardinality = cardinality
        # One retained point per datum (POL-CAT-083): the datum is private computation
        # data inside the set's boundary (POL-TYPE-012), so these tables never key on
        # an owned value.  A datum whose engine equality is Boolean-exact keys the
        # first table by value, so two equal data select one point.  A datum whose
        # equality can be ``Unknown`` (a rule-defined family, the name of a map with an
        # unenumerated domain) is retained by identity in the second: two distinct
        # such data yield two points, which are ``True``-equal and hash-equal exactly
        # when the engine later decides their data equal.
        self._points: dict[Datum, SetPoint] = {}
        self._rule_points: MonoDict = MonoDict()

    def membership_proposition(self, candidate: CategoryPoint) -> AppliedPredicate:
        return element_of(candidate, self)

    def __contains__(self, candidate: Any) -> bool:
        decision = ask(element_of(candidate, self))
        if decision is Unknown:
            logger.info("membership of %r in %r was not established", candidate, self)
            return False
        return decision is True

    def point(self, datum: Datum) -> SetPoint:
        """The classical element ``1 -> X`` selecting ``datum``, one point per datum."""
        assert self._membership_rule(datum) is not False, f"{datum!r} is not a member of {self!r}"
        table = self._points if isinstance(datum == datum, bool) else self._rule_points
        if datum not in table:
            sets = _sets.Sets()
            defining_morphism = sets.construct_morphism(sets.Terminal(), self, lambda star: datum)
            table[datum] = self.category().ElementType(defining_morphism, datum)
        return table[datum]

    def cardinality(self) -> CardinalObject | UnknownClass:
        return self._cardinality

    def subset_from(self, predicate: MembershipRule) -> SetObject:
        """The chosen subset ``{x in X : predicate(x)}`` with its retained inclusion (POL-SET-007, POL-ENGINE-004).

        The predicate is a datum-level rule, the form of ``Sets()(rule)``; the
        construction is owned by ``Sets().ChosenSubsets()`` (``sets/subobjects.py``).
        """
        return _sets.Sets().ChosenSubsets()(self, predicate)

    def is_finite(self) -> AppliedPredicate:
        return _sets.Sets().Finite().predicate()(self)

    def is_infinite(self) -> AppliedPredicate:
        return _sets.Sets().Infinite().predicate()(self)

    def is_countable(self) -> AppliedPredicate:
        return _sets.Sets().Countable().predicate()(self)

    def is_uncountable(self) -> AppliedPredicate:
        return _sets.Sets().Uncountable().predicate()(self)

    def __repr__(self) -> str:
        finite = _sets.Sets().Finite()
        if finite.has_chosen_enumeration(self):
            return "{" + ", ".join(map(repr, finite.chosen_enumeration(self))) + "}"
        return "Set(<rule>)"


class FiniteSetRole(ObjectOfCategory):
    """The local object role of ``Sets().Finite()``: the chosen enumeration supplies iteration."""

    def __init__(self, category: Category, members: tuple[Datum, ...]) -> None:
        super().__init__(
            category,
            lambda datum: any(datum == member for member in members),
            Cardinal()(len(members)),
        )

    def __iter__(self) -> Iterator[SetPoint]:
        return (self.point(datum) for datum in _sets.Sets().Finite().chosen_enumeration(self))
