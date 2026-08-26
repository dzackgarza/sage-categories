"""The function set ``Y ** X`` of ``Sets()`` (D02, POL-SET-017/020).

``Sets()`` is cartesian closed: the exponential ``Y ** X`` is the function set, the
rule-defined set whose points are the maps ``X -> Y``, retained once per pair
(Mathlib ``CategoryTheory.Types.instCartesianClosed``; inspected 2026-08-26).  It
retains the evaluation morphism ``ev: (Y ** X) * X -> Y`` and, for a map ``f``, its
name ``1 -> Y ** X`` (Mac Lane and Moerdijk, *Sheaves in Geometry and Logic*,
I.6, the name of an arrow; inspected 2026-08-26).  ``Mor(Sets())(X, Y)`` is the
discrete category on these points.  The cardinality is ``(#Y) ** (#X)`` when both
cardinals are exact (Mathlib ``Cardinal.power_def``; inspected 2026-08-26) and
``Unknown`` otherwise.
"""

from __future__ import annotations

from typing import Any

from sage.structure.coerce_dict import TripleDict

import sage_categories.sets.category as _sets
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import ask
from sage_categories.sets.elements import Datum, SetPoint
from sage_categories.sets.maps import SetMap
from sage_categories.sets.objects import SetObject

__all__ = ["Function", "evaluation_morphism", "function_set", "name_of"]


class Function:
    """The private datum of a point of ``Y ** X``: the map it names.

    This is private computation data, not an owned value (D17 governs owned
    values).  Two names compare through map equality: exact when the domain has a
    chosen enumeration, and then the hash is the hash of the tuple of image data, so
    equal names hash equal; otherwise equality is ``Unknown`` except on identity and
    the hash is by identity.
    """

    def __init__(self, set_map: SetMap) -> None:
        self._map = set_map

    def map(self) -> SetMap:
        return self._map

    def _images(self) -> tuple[Datum, ...] | UnknownClass:
        finite = _sets.Sets().Finite()
        if not finite.has_chosen_enumeration(self._map.domain()):
            return Unknown
        return tuple(self._map._rule(datum) for datum in finite.chosen_enumeration(self._map.domain()))

    def __eq__(self, other: Any) -> Decision:
        if other is self:
            return True
        match other:
            case Function():
                return ask(self._map == other.map())
            case _:
                return False

    def __hash__(self) -> int:
        images = self._images()
        if images is Unknown:
            return object.__hash__(self)
        return hash(images)

    def __repr__(self) -> str:
        return f"name of {self._map!r}"


_function_sets: TripleDict = TripleDict(weak_values=False)
_evaluations: TripleDict = TripleDict(weak_values=False)


def function_set(exponent: SetObject, base: SetObject) -> SetObject:
    """``base ** exponent``: the set of maps ``exponent -> base``, retained per pair."""
    sets = _sets.Sets()
    key = (exponent, base, sets)
    if key not in _function_sets:
        maps = sets.morphism_category(1)(exponent, base)

        def membership_rule(datum: Datum) -> Decision:
            match datum:
                case Function():
                    return ask(maps.membership_proposition(datum.map()))
                case _:
                    return False

        base_cardinality, exponent_cardinality = base.cardinality(), exponent.cardinality()
        cardinality = base_cardinality**exponent_cardinality if base_cardinality is not Unknown and exponent_cardinality is not Unknown else Unknown
        _function_sets[key] = sets.ObjectType(sets, membership_rule, cardinality)
    return _function_sets[key]


def name_of(set_map: SetMap) -> SetPoint:
    """The point ``1 -> Y ** X`` naming a map ``X -> Y``."""
    return function_set(set_map.domain(), set_map.codomain()).point(Function(set_map))


def evaluation_morphism(exponent: SetObject, base: SetObject) -> SetMap:
    """``ev: (Y ** X) * X -> Y``, retained per pair."""
    sets = _sets.Sets()
    key = (exponent, base, sets)
    if key not in _evaluations:
        product = sets.Products()((function_set(exponent, base), exponent))
        _evaluations[key] = sets.construct_morphism(product.apex(), base, lambda family: family(0).map()._rule(family(1)))
    return _evaluations[key]
