"""``Sets()`` products and coproducts over discrete shapes, with their cardinality case trees (POL-SET-013/020/021).

The product of ``D: Discrete(S) -> Sets()`` is the set of ``S``-indexed families
``i |-> x_i`` with ``x_i in D(i)``, a point given by a rule on the index data and
never enumerated; its projections evaluate a family at ``i`` and the mediator of
a cone ``(N, c_i)`` sends ``n`` to the family ``i |-> c_i(n)`` (Mathlib
``CategoryTheory.Limits.Types.productLimitCone``; inspected 2026-08-26).  The
coproduct is the set of tagged points ``(i, x)`` with ``x in D(i)``; its
injections tag and the mediator of a cocone ``(N, c_i)`` sends ``(i, x)`` to
``c_i(x)`` (Mathlib ``CategoryTheory.Limits.Types.coproductColimitCocone``;
inspected 2026-08-26).  When the index set and every factor carry a chosen
enumeration, the apex is constructed through ``Sets().Finite()`` and retains
its enumeration.

Cardinality is a computational case tree routed on the retained data
(POL-MATH-042), each case citing its theorem (all Mathlib, inspected 2026-08-26):

- a finite enumerated index with every factor cardinality exact gives the exact
  product (``Cardinal.mk_pi`` with ``Cardinal.prod`` over a finite type,
  ``Fintype.card_pi``);
- a finite enumerated index with a factor of cardinality ``0`` gives ``0``
  (``Cardinal.prod_eq_zero``);
- the constant diagram at ``X`` over ``S`` with both cardinals exact gives
  ``(#X) ** (#S)`` (``Cardinal.prod_const'``);
- an infinite index with the diagram's codomain in ``Sets().Uncountable()``
  places the product in ``Sets().Uncountable()``: each factor has at least two
  points, so ``2 ** #S <= prod`` (``Cardinal.prod_le_prod``) and ``#S < 2 ** #S``
  (``Cardinal.cantor``) with ``aleph0 <= #S``;
- a finite index with codomain in ``Sets().Countable()`` places the product in
  ``Sets().Countable()`` (the instance ``[Finite α] [∀ a, Countable (π a)] :
  Countable (∀ a, π a)`` of ``Mathlib/Data/Countable/Basic.lean``);
- otherwise ``Unknown``.

Coproducts use the dual sums: an enumerated index with every cofactor exact gives
the exact sum (``Cardinal.mk_sigma``, ``Fintype.card_sigma``); the constant
diagram at ``X`` gives ``(#S) * (#X)`` (``Cardinal.sum_const'``); an infinite
index with codomain in ``Sets().Uncountable()`` places the coproduct in
``Sets().Uncountable()`` (``Cardinal.le_sum``: a cofactor injects); a countable
index with codomain in ``Sets().Countable()`` places it in ``Sets().Countable()``
(the instance ``[Countable α] [∀ a, Countable (π a)] : Countable (Sigma π)`` of
``Mathlib/Data/Countable/Basic.lean``); otherwise ``Unknown``.  The empty-factor case of
products has no nontrivial dual: an empty cofactor contributes ``0`` to an exact
sum.
"""

from __future__ import annotations

import itertools
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from sage.misc.cachefunc import cached_function

import sage_categories.sets.category as _sets
from sage_categories.cat.constructions import cocone, cocone_apex, cone, cone_apex
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.shapes import DiscreteCategory, index_set_of
from sage_categories.cat.predicates import Decision, Unknown, UnknownClass
from sage_categories.cat.predicates import ask, conjunction, established, negation
from sage_categories.kernel.refinement import is_subcategory, refine
from sage_categories.sets.cardinals import Cardinal, CardinalObject
from sage_categories.sets.elements import Datum
from sage_categories.sets.objects import SetObject

if TYPE_CHECKING:
    from sage_categories.sets.category import SetMap

__all__ = ["Family", "coproduct_of_sets", "product_of_sets"]


class Family:
    """The private datum of a point of a product: an indexed family of data by rule.

    This is private computation data, not an owned value (POL-SET-026 governs owned
    values).  Two families over one finitely enumerated index set compare
    componentwise, exactly, and then hash by the tuple of components, so equal
    families hash equal; over any other index set equality is ``Unknown`` except on
    identity and the hash is by identity.
    """

    def __init__(self, index_set: SetObject, rule: Callable[[Datum], Datum]) -> None:
        self._index_set = index_set
        self._rule = rule

    def index_set(self) -> SetObject:
        return self._index_set

    def __call__(self, index_datum: Datum) -> Datum:
        return self._rule(index_datum)

    def _enumeration(self) -> tuple[Datum, ...] | UnknownClass:
        finite = _sets.Sets().Finite()
        if not finite.has_chosen_enumeration(self._index_set):
            return Unknown
        return finite.chosen_enumeration(self._index_set)

    def __eq__(self, other: Any) -> Decision:
        if other is self:
            return True
        match other:
            case Family():
                if other.index_set() is not self._index_set:
                    return False
            case _:
                return False
        enumeration = self._enumeration()
        if enumeration is Unknown:
            return Unknown
        return ask(conjunction(self(datum) == other(datum) for datum in enumeration))

    def __hash__(self) -> int:
        enumeration = self._enumeration()
        if enumeration is Unknown:
            return object.__hash__(self)
        return hash(tuple(self(datum) for datum in enumeration))

    def __repr__(self) -> str:
        enumeration = self._enumeration()
        if enumeration is Unknown:
            return "family(<rule>)"
        return "(" + ", ".join(repr(self(datum)) for datum in enumeration) + ")"


def _index_datum(vertex: DiscreteCategory.ObjectType) -> Datum:
    return vertex.point()._point_datum_()


def _exact(cardinality: CardinalObject | UnknownClass) -> bool:
    return cardinality is not Unknown


# -- products ---------------------------------------------------------------------------------


def _product_cardinality(diagram: Functor, index_set: SetObject, factors: tuple[SetObject, ...] | UnknownClass) -> CardinalObject | UnknownClass:
    """The product cardinality case tree; ``factors`` is the enumerated family when the index is enumerated."""
    if factors is not Unknown:
        cardinalities = tuple(factor.cardinality() for factor in factors)
        if all(map(_exact, cardinalities)):
            # Cardinal.mk_pi, Fintype.card_pi: the exact finite product.
            return Cardinal()(_cardinal_product(cardinalities))
        if any(_exact(cardinality) and established(cardinality == 0) for cardinality in cardinalities):
            # Cardinal.prod_eq_zero: a factor of cardinality 0.
            return Cardinal()(0)
    functors = Fun(diagram.domain(), diagram.codomain())
    if functors.has_constant_value(diagram):
        value_cardinality, index_cardinality = functors.constant_value(diagram).cardinality(), index_set.cardinality()
        if _exact(value_cardinality) and _exact(index_cardinality):
            # Cardinal.prod_const': prod (fun _ => a) = a ^ #S.
            return value_cardinality**index_cardinality
    return Unknown


def _cardinal_product(cardinalities: tuple[CardinalObject, ...]) -> CardinalObject | int:
    product: CardinalObject | int = 1
    for cardinality in cardinalities:
        product = product * cardinality
    return product


def _product_placements(diagram: Functor, index_set: SetObject) -> tuple[_sets.Category, ...]:
    """The property categories the product enters by its case tree."""
    sets = _sets.Sets()
    if established(index_set.is_infinite()) and is_subcategory(diagram.codomain(), sets.Uncountable()):
        # Cardinal.prod_le_prod with Cardinal.cantor: 2 ** #S <= prod and #S < 2 ** #S.
        return (sets.Uncountable(),)
    if established(index_set.is_finite()) and is_subcategory(diagram.codomain(), sets.Countable()):
        # A product of countably many countable sets over a finite index is countable:
        # Mathlib ``instance [Finite α] [∀ a, Countable (π a)] : Countable (∀ a, π a)``
        # (``Mathlib/Data/Countable/Basic.lean``; inspected 2026-08-27).  Finiteness of
        # the index is what the instance needs, not a chosen enumeration.
        return (sets.Countable(),)
    return ()


def product_of_sets(diagram: Functor) -> SetObject:
    """``Sets().Products()(diagram)`` for ``diagram: Discrete(S) -> Sets()``: the set of ``S``-indexed families."""
    sets, finite = _sets.Sets(), _sets.Sets().Finite()
    shape = diagram.domain()
    index_set = index_set_of(shape)
    enumerated = finite.has_chosen_enumeration(index_set)

    def factor(index_datum: Datum) -> SetObject:
        return diagram.on_object(shape(index_set.point(index_datum)))

    factors: tuple[SetObject, ...] | UnknownClass = (
        tuple(factor(datum) for datum in finite.chosen_enumeration(index_set)) if enumerated else Unknown
    )

    def membership_rule(datum: Datum) -> Decision:
        match datum:
            case Family() if datum.index_set() is index_set:
                if factors is Unknown:
                    return Unknown
                return ask(conjunction(factor._set_object_data.membership_rule(datum(index)) for index, factor in zip(finite.chosen_enumeration(index_set), factors)))
            case _:
                return False

    if factors is not Unknown and all(finite.has_chosen_enumeration(factor) for factor in factors):
        enumeration = finite.chosen_enumeration(index_set)
        choices = itertools.product(*(finite.chosen_enumeration(factor) for factor in factors))
        apex = finite(Family(index_set, dict(zip(enumeration, choice)).__getitem__) for choice in choices)
    else:
        apex = sets.rule_valued(membership_rule, _product_cardinality(diagram, index_set, factors))
        for placement in _product_placements(diagram, index_set):
            refine(apex, placement)

    @cached_function(key=lambda vertex: (id(vertex), vertex))
    def projection(vertex: DiscreteCategory.ObjectType) -> SetMap:
        index_datum = _index_datum(vertex)
        return sets.construct_morphism(apex, diagram.on_object(vertex), lambda family: family(index_datum))

    def mediator(candidate_cone: NaturalTransformation) -> SetMap:
        source = cone_apex(candidate_cone)
        return sets.construct_morphism(
            source,
            apex,
            lambda source_datum: Family(
                index_set,
                lambda index_datum: candidate_cone.component(shape(index_set.point(index_datum)))._set_morphism_data.rule(source_datum),
            ),
        )

    lowered = sets.Products().lowered(diagram)
    return sets.Products().with_universal_data(lowered, apex, cone(lowered, apex, projection), mediator)


# -- coproducts -------------------------------------------------------------------------------


def _coproduct_cardinality(diagram: Functor, index_set: SetObject, cofactors: tuple[SetObject, ...] | UnknownClass) -> CardinalObject | UnknownClass:
    """The coproduct cardinality case tree, dual to the product tree."""
    if cofactors is not Unknown:
        cardinalities = tuple(cofactor.cardinality() for cofactor in cofactors)
        if all(map(_exact, cardinalities)):
            # Cardinal.mk_sigma, Fintype.card_sigma: the exact finite sum.
            return Cardinal()(sum(cardinalities, 0))
    functors = Fun(diagram.domain(), diagram.codomain())
    if functors.has_constant_value(diagram):
        value_cardinality, index_cardinality = functors.constant_value(diagram).cardinality(), index_set.cardinality()
        if _exact(value_cardinality) and _exact(index_cardinality):
            # Cardinal.sum_const': sum (fun _ => a) = #S * a.
            return index_cardinality * value_cardinality
    return Unknown


def _coproduct_placements(diagram: Functor, index_set: SetObject) -> tuple[_sets.Category, ...]:
    sets = _sets.Sets()
    if established(index_set.is_infinite()) and is_subcategory(diagram.codomain(), sets.Uncountable()):
        # Cardinal.le_sum: an uncountable cofactor injects into the coproduct.
        return (sets.Uncountable(),)
    if established(index_set.is_countable()) and is_subcategory(diagram.codomain(), sets.Countable()):
        # A countable union of countable sets is countable: Mathlib ``instance [Countable α]
        # [∀ a, Countable (π a)] : Countable (Sigma π)`` (``Mathlib/Data/Countable/Basic.lean``;
        # inspected 2026-08-27).
        return (sets.Countable(),)
    return ()


def coproduct_of_sets(diagram: Functor) -> SetObject:
    """``Sets().Coproducts()(diagram)`` for ``diagram: Discrete(S) -> Sets()``: the set of tagged points ``(i, x)``."""
    sets, finite = _sets.Sets(), _sets.Sets().Finite()
    shape = diagram.domain()
    index_set = index_set_of(shape)
    enumerated = finite.has_chosen_enumeration(index_set)

    def cofactor(index_datum: Datum) -> SetObject:
        return diagram.on_object(shape(index_set.point(index_datum)))

    cofactors: tuple[SetObject, ...] | UnknownClass = (
        tuple(cofactor(datum) for datum in finite.chosen_enumeration(index_set)) if enumerated else Unknown
    )

    def membership_rule(datum: Datum) -> Decision:
        match datum:
            case (index_datum, value):
                index_decision = index_set._set_object_data.membership_rule(index_datum)
                if established(negation(index_decision)):
                    return False
                return ask(conjunction((index_decision, cofactor(index_datum)._set_object_data.membership_rule(value))))
            case _:
                return False

    if cofactors is not Unknown and all(finite.has_chosen_enumeration(cofactor) for cofactor in cofactors):
        apex = finite(
            (index_datum, value)
            for index_datum, cofactor in zip(finite.chosen_enumeration(index_set), cofactors)
            for value in finite.chosen_enumeration(cofactor)
        )
    else:
        cardinality = _coproduct_cardinality(diagram, index_set, cofactors)
        apex = sets(membership_rule) if cardinality is Unknown else sets.with_cardinality(membership_rule, cardinality)
        for placement in _coproduct_placements(diagram, index_set):
            refine(apex, placement)

    @cached_function(key=lambda vertex: (id(vertex), vertex))
    def injection(vertex: DiscreteCategory.ObjectType) -> SetMap:
        index_datum = _index_datum(vertex)
        return sets.construct_morphism(diagram.on_object(vertex), apex, lambda value: (index_datum, value))

    def mediator(candidate_cocone: NaturalTransformation) -> SetMap:
        target = cocone_apex(candidate_cocone)
        return sets.construct_morphism(
            apex,
            target,
            lambda tagged: candidate_cocone.component(shape(index_set.point(tagged[0])))._set_morphism_data.rule(tagged[1]),
        )

    lowered = sets.Coproducts().lowered(diagram)
    return sets.Coproducts().with_universal_data(lowered, apex, cocone(lowered, apex, injection), mediator)
