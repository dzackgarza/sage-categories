"""The function set ``Y ** X`` of ``Sets()``.

``Sets()`` realizes the exponential as the rule-defined set of maps ``X -> Y``,
retained once per pair. It retains the evaluation morphism
``ev: (Y ** X) * X -> Y``, the transpose ``Z -> Y ** X`` of a map ``Z * X -> Y``,
and the name ``* -> Y ** X`` of a map ``X -> Y``.
``Mor(Sets())(X, Y)`` is the discrete category on these points.
The cardinality is ``(#Y) ** (#X)`` when both cardinals are exact and ``Unknown``
otherwise.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sage.misc.cachefunc import cached_function

import sage_categories.sets.category as _sets
from sage_categories.cat.constructions import cone
from sage_categories.cat.diagrams import sequence_position
from sage_categories.cat.predicates import Decision, Unknown, UnknownClass
from sage_categories.cat.predicates import ask
from sage_categories.sets.elements import Datum, SetElement
from sage_categories.sets.objects import SetObject

if TYPE_CHECKING:
    from sage_categories.sets.category import SetMap

__all__ = ["Function", "evaluation_morphism", "function_set", "name_of", "transpose"]


class Function:
    """The private datum of a point of ``Y ** X``: the map it names.

    This is private computation data, not an owned value (POL-SET-026 governs owned
    values).  Two names of one map are equal; two names compare through map
    equality otherwise, exact when the domain has a chosen enumeration and
    ``Unknown`` else.  The hash is the hash of the tuple of image data when the
    domain is enumerated and the hash of the named map otherwise, so equal names
    hash equal.
    """

    def __init__(self, set_map: SetMap) -> None:
        self._map = set_map

    def map(self) -> SetMap:
        return self._map

    def _images(self) -> tuple[Datum, ...] | UnknownClass:
        finite = _sets.Sets().Finite()
        if not finite.has_chosen_enumeration(self._map.domain()):
            return Unknown
        rule = self._map._set_morphism_data.rule
        return tuple(rule(datum) for datum in finite.chosen_enumeration(self._map.domain()))

    def __eq__(self, other: Any) -> Decision:
        match other:
            case Function():
                return ask(self._map == other.map())
            case _:
                return False

    def __hash__(self) -> int:
        images = self._images()
        if images is Unknown:
            return hash(self._map)
        return hash(images)

    def __repr__(self) -> str:
        return f"name of {self._map!r}"


@cached_function(key=lambda exponent, base: ((id(exponent), exponent), (id(base), base)))
def function_set(exponent: SetObject, base: SetObject) -> SetObject:
    """``base ** exponent``: the set of maps ``exponent -> base``, retained per pair."""
    sets = _sets.Sets()
    maps = sets.morphism_category(1)(exponent, base)

    def membership_rule(datum: Datum) -> Decision:
        match datum:
            case Function():
                return ask(maps.membership_proposition(datum.map()))
            case _:
                return False

    base_cardinality, exponent_cardinality = base.cardinality(), exponent.cardinality()
    cardinality = base_cardinality**exponent_cardinality if base_cardinality is not Unknown and exponent_cardinality is not Unknown else Unknown
    return sets.rule_valued(membership_rule, cardinality)


def name_of(set_map: SetMap) -> SetElement:
    """The point ``* -> Y ** X`` naming a map ``X -> Y``."""
    return function_set(set_map.domain(), set_map.codomain()).point(Function(set_map))


@cached_function(key=lambda exponent, base: ((id(exponent), exponent), (id(base), base)))
def evaluation_morphism(exponent: SetObject, base: SetObject) -> SetMap:
    """``ev: (Y ** X) * X -> Y``, retained per pair."""
    sets = _sets.Sets()
    product = sets.Products()((function_set(exponent, base), exponent))
    return sets.construct_morphism(product, base, lambda family: family(0).map()._set_morphism_data.rule(family(1)))


@cached_function(key=lambda set_map: (id(set_map), set_map))
def transpose(set_map: SetMap) -> SetMap:
    """The transpose ``Z -> Y ** X`` of ``f: Z * X -> Y``, retained per map.

    Its value at ``z`` names the composite ``f after <z, id_X>: X -> Y``, where
    ``<z, id_X>: X -> Z * X`` is the mediating map of the cone ``(constant at z,
    identity)`` (Mac Lane, *Categories for the Working Mathematician*, IV.6, the
    exponential transpose; inspected 2026-08-27).
    """
    sets = _sets.Sets()
    product, base = set_map.domain(), set_map.codomain()
    assert product in sets.Products(), f"{product!r} is not a chosen product"
    source, exponent = product.product_projection(0).codomain(), product.product_projection(1).codomain()
    assert product is sets.Products()((source, exponent)), f"{product!r} is not the chosen binary product {source!r} * {exponent!r}"

    def transposed(source_datum: Datum) -> Function:
        constant = sets.construct_morphism(exponent, source, lambda exponent_datum: source_datum)
        legs = {0: constant, 1: exponent.identity()}
        pairing = product.universal_morphism(cone(product.diagram(), exponent, lambda vertex: legs[sequence_position(vertex)]))
        return Function(set_map * pairing)

    return sets.construct_morphism(source, function_set(exponent, base), transposed)
