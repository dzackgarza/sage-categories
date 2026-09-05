"""Sets equipped with a binary relation, and their partial-order subcategory.

An object of ``BinaryRelations()`` is a set ``X`` together with the data of a
relation ``R <= X * X`` (Mathlib ``CategoryTheory`` relation objects; a poset is a
set with such data, not a relation).  Its structure functor to ``Sets()`` forgets the
relation, so a relation object inherits point, map, and set behavior from its carrier.
``Posets()`` is the ``PartialOrder`` property subcategory of ``BinaryRelations()``.
"""

from __future__ import annotations

__all__ = ["BinaryRelations", "BinaryRelationsCategory", "Posets", "PosetsCategory", "TotallyOrderedSets"]

from collections.abc import Callable

from sympy.logic.boolalg import Boolean

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.predicates import Axiom, Predicate, Proposition, ask, register_handler
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.sage_runtime import cached_function

type OrderRule = Callable[[CategoryOfCategories.ElementType, CategoryOfCategories.ElementType], Proposition]


class _OrderRelatedPredicate(Predicate):
    name = "order_related"


class _PartialOrderPredicate(Predicate):
    name = "partial_order"


class _TotalOrderPredicate(Predicate):
    name = "total_order"


order_related = _OrderRelatedPredicate()
partial_order = _PartialOrderPredicate()
total_order = _TotalOrderPredicate()


def _related_pairs(relation_object: BinaryRelationsCategory.ObjectType) -> frozenset[tuple[object, object]]:
    """The finite set of related data pairs of a relation object."""
    return frozenset(point.datum() for point in relation_object.relation().arrow().domain())


def _decide_order_related(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    assumptions: Proposition,
) -> bool:
    """Whether the ordered pair ``(first, second)`` lies in its object's relation."""
    return (first.datum(), second.datum()) in _related_pairs(first.parent())


def _decide_partial_order(
    relation_object: BinaryRelationsCategory.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    """Reflexivity, antisymmetry, and transitivity of a finite relation (Mathlib ``PartialOrder``)."""
    carrier = relation_object.carrier()
    data = tuple(point.datum() for point in carrier)
    pairs = _related_pairs(relation_object)
    reflexive = all((value, value) in pairs for value in data)
    antisymmetric = all(
        first == second
        for first in data
        for second in data
        if (first, second) in pairs and (second, first) in pairs
    )
    transitive = all(
        (first, third) in pairs
        for first in data
        for second in data
        for third in data
        if (first, second) in pairs and (second, third) in pairs
    )
    return reflexive and antisymmetric and transitive


class BinaryRelationsCategory(Category[[MorphismCategory.ObjectType], []]):
    """Sets equipped with a binary endorelation, and relation-preserving maps."""

    class ObjectType:
        def __init__(self, relation: CategoryOfCategories.ElementType) -> None:
            self._relation = relation
            self._carrier = relation.arrow().codomain().product_projection(0).codomain()

        def relation(self) -> CategoryOfCategories.ElementType:
            return self._relation

        def carrier(self) -> CategoryOfCategories.ElementType:
            return self._carrier

        def related(
            self,
            first: CategoryOfCategories.ElementType,
            second: CategoryOfCategories.ElementType,
        ) -> Proposition:
            """The proposition that ``first`` and ``second`` stand in the relation."""
            return order_related(first, second)

    class ElementType:
        """A point of the carrier, inherited through the structure functor to ``Sets()``."""

    class MorphismType:
        def __init__(self, underlying: MorphismCategory.ObjectType) -> None:
            self._underlying_map = underlying

        def underlying_map(self) -> MorphismCategory.ObjectType:
            return self._underlying_map

    def _partial_order(self, relation_object: BinaryRelationsCategory.ObjectType) -> Proposition:
        return partial_order(relation_object)

    PartialOrder = Axiom(_partial_order)

    def __repr__(self) -> str:
        return "BinaryRelations"

    def __call__(self, relation: CategoryOfCategories.ElementType) -> BinaryRelationsCategory.ObjectType:
        return self.ObjectType(relation)

    def from_predicate(
        self,
        carrier: CategoryOfCategories.ElementType,
        rule: OrderRule,
    ) -> BinaryRelationsCategory.ObjectType:
        """The relation object whose relation ``rule`` selects in ``carrier * carrier``."""
        product = Sets.Products()((carrier, carrier))

        def pair_rule(pair: CategoryOfCategories.ElementType) -> Boolean:
            first, second = pair.datum()
            return rule(carrier.point(first), carrier.point(second))

        subobject = Sets.Subobjects(product).from_predicate(pair_rule)
        return self.ObjectType(subobject)

    def to_sets(self) -> Functor:
        """The faithful isofibration ``(X, R) |-> X`` forgetting the relation (D163)."""
        return Fun(self, Sets).Faithful().Isofibrations()(
            lambda relation_object: relation_object._carrier,
            lambda arrow: arrow._underlying_map,
        )

    def structure_functors(self) -> tuple[Functor, ...]:
        return (self.to_sets(),)

    def construct_morphism(
        self,
        source: BinaryRelationsCategory.ObjectType,
        target: BinaryRelationsCategory.ObjectType,
        underlying: MorphismCategory.ObjectType,
    ) -> BinaryRelationsCategory.MorphismType:
        assert underlying.domain() is source._carrier and underlying.codomain() is target._carrier
        images = {value: underlying._action(value) for value in (point.datum() for point in source._carrier)}
        target_pairs = _related_pairs(target)
        assert all(
            (images[first], images[second]) in target_pairs for first, second in _related_pairs(source)
        ), f"{underlying!r} does not preserve the relation of {source!r}"
        return self.MorphismType(domain=source, codomain=target, data=underlying)

    def construct_identity(self, relation_object: BinaryRelationsCategory.ObjectType) -> BinaryRelationsCategory.MorphismType:
        return self.MorphismType(
            domain=relation_object,
            codomain=relation_object,
            data=Mor(Sets)(relation_object._carrier, relation_object._carrier).one(),
        )

    def composite(
        self,
        second: BinaryRelationsCategory.MorphismType,
        first: BinaryRelationsCategory.MorphismType,
    ) -> BinaryRelationsCategory.MorphismType:
        return self.MorphismType(
            domain=first.domain(),
            codomain=second.codomain(),
            data=second._underlying_map * first._underlying_map,
        )


class PosetsCategory(PropertySubcategory[[MorphismCategory.ObjectType], []]):
    """``BinaryRelations().PartialOrder()``: relation objects whose relation is a partial order."""

    _base_category_class_and_axiom = (BinaryRelationsCategory, "PartialOrder")

    class ObjectType:
        """A partial order: a relation object satisfying the order laws (POL-CAT-079)."""

    class ElementType:
        """A point of a poset, comparable through its owned order."""

        def __le__(self, other: CategoryOfCategories.ElementType) -> Proposition:
            return self.parent().related(self, other)

    class MorphismType:
        """A monotone map: a relation-preserving map between two posets."""

    def _total(self, poset_object: CategoryOfCategories.ElementType) -> Proposition:
        return total_order(poset_object)

    Total = Axiom(_total)


@cached_function(key=lambda: 0)
def BinaryRelations() -> BinaryRelationsCategory:
    """The category of sets equipped with a binary relation."""
    return BinaryRelationsCategory()


def Posets() -> Category:
    """The category of partial orders: ``BinaryRelations().PartialOrder()``."""
    return BinaryRelations().PartialOrder()


def TotallyOrderedSets() -> Category:
    """The category of total orders: ``Posets().Total()``."""
    return Posets().Total()


def _decide_total_order(
    poset_object: BinaryRelationsCategory.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    """Totality of a finite order: every pair of carrier points is comparable."""
    data = tuple(point.datum() for point in poset_object.carrier())
    pairs = _related_pairs(poset_object)
    return all((first, second) in pairs or (second, first) in pairs for first in data for second in data)


register_handler(order_related, _decide_order_related)
register_handler(partial_order, _decide_partial_order)
register_handler(total_order, _decide_total_order)
