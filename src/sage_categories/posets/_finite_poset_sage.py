"""The private Sage boundary of ``FinitePosets()`` (POL-LAYOUT-020, POL-LEAF-044/046).

A finite poset is lowered once to a Sage finite poset on the enumeration data of its
underlying set (Sage ``Poset((elements, relation), facade=True)``: ``relation(x, y)`` is
``x <= y`` and the elements are the data themselves; inspected 2026-08-27).  The
lowering of a point is its datum, and ``element`` reconstructs the
point over a datum.  Nothing here is public mathematics.
"""

from __future__ import annotations

from collections.abc import Iterable

from sage.combinat.posets.posets import FinitePoset as SagePoset, Poset as sage_poset_constructor
from sage.rings.integer import Integer
from sage.structure.coerce_dict import MonoDict

import sage_categories.posets.category as _posets
from sage_categories.kernel.decisions import Unknown
from sage_categories.kernel.predicates import ask, disjunction
from sage_categories.posets.category import Poset, PosetElement
from sage_categories.sets.category import Sets
from sage_categories.sets.elements import Datum
from sage_categories.sets.objects import MembershipRule, SetObject

__all__ = ["count", "data", "datum", "element", "sage_poset", "selecting"]

_sage_posets: MonoDict = MonoDict()


def _carrier(poset: Poset) -> SetObject:
    return _posets.Posets().underlying_set_functor().on_object(poset)


def sage_poset(poset: Poset) -> SagePoset:
    """The Sage finite poset on the enumeration data of ``U(P)``, constructed once."""
    if poset not in _sage_posets:
        carrier = _carrier(poset)
        data = Sets().Finite().chosen_enumeration(carrier)

        def at_most(left: Datum, right: Datum) -> bool:
            decision = ask(poset.element(carrier.point(left)) <= poset.element(carrier.point(right)))
            assert decision is not Unknown, f"the order of {poset!r} is undecided on {left!r}, {right!r}"
            return decision

        _sage_posets[poset] = sage_poset_constructor((data, at_most), facade=True)
    return _sage_posets[poset]


def datum(poset: Poset, member: PosetElement) -> Datum:
    """The enumeration datum of a point of ``P``."""
    carrier = _carrier(poset)
    point = _posets.Posets().underlying_set_functor().on_element(member)
    assert point.parent() is carrier, f"{member!r} is not an element of {poset!r}"
    return next(candidate for candidate in Sets().Finite().chosen_enumeration(carrier) if carrier.point(candidate) is point)


def data(poset: Poset, members: Poset) -> tuple[Datum, ...]:
    """The enumeration data of a sub-poset ``A`` of ``P``: ``U(A)`` is a chosen subset of ``U(P)``."""
    carrier = _carrier(members)
    assert carrier.monomorphism().codomain() is _carrier(poset), f"{members!r} is not a sub-poset of {poset!r}"
    return Sets().Finite().chosen_enumeration(carrier)


def element(poset: Poset, value: Datum) -> PosetElement:
    """The point of ``P`` over the point selecting an enumeration datum."""
    return poset.element(_carrier(poset).point(value))


def selecting(data: Iterable[Datum]) -> MembershipRule:
    """The membership rule selecting finitely many enumeration data.

    The disjunction is asked: ``==`` on an owned datum returns a proposition, not a
    decision (POL-MATH-034/035), and a ``MembershipRule`` returns a ``Decision``.
    """
    selected = tuple(data)
    return lambda candidate: ask(disjunction(candidate == value for value in selected))


def count(value: Integer) -> int:
    # Sage returns a Sage integer; ``Cardinal()`` takes the Python integer at its boundary.
    return int(value)
