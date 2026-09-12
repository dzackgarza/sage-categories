"""Sets equipped with a binary relation, and their partial-order subcategory.

An object of ``BinaryRelations()`` is a set ``X`` together with the data of a
relation ``R <= X * X`` (Mathlib ``CategoryTheory`` relation objects; a poset is a
set with such data, not a relation).  Its structure functor to ``Sets()`` forgets the
relation, so a relation object inherits point, map, and set behavior from its carrier.
``Posets()`` is the ``PartialOrder`` property subcategory of ``BinaryRelations()``.
"""

from __future__ import annotations

__all__ = ["BinaryRelations", "BinaryRelationsCategory", "Posets", "PosetsCategory", "Thin", "TotallyOrderedSets"]

from collections.abc import Callable

from sympy import ask as sympy_ask
from sympy.logic.boolalg import Boolean

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Cat, Fun, Functor
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.predicates import (
    Axiom,
    Predicate,
    Proposition,
    conjunction,
    register_handler,
)
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.cat.shapes import Discrete, ThinCategory
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


def _square_factor(square: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    """The set ``X`` of a chosen set product ``X * X``, read from its presenting diagrams.

    One chosen set can present several diagrams: the pair space of a two-element carrier
    is also the product of two two-element chains, so ``ApexCategory.presentation`` names
    both and directs the caller to the diagrams themselves (``cat/constructions.py``).
    """
    family = Sets.Products().presenting_family(square)
    factors = tuple(diagram.on_object(diagram.domain()(0)) for diagram in family.presenting_diagrams(square))
    assert all(factor is factors[0] for factor in factors), f"{square!r} presents products of unequal sets"
    return factors[0]


def _related_pairs(relation_object: BinaryRelationsCategory.ObjectType) -> frozenset[tuple[object, object]]:
    """The finite set of related data pairs of a relation object."""
    return frozenset(point.datum() for point in relation_object.relation().arrow().domain())


def _decide_order_related(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    assumptions: Proposition,
) -> bool | None:
    """Whether the ordered pair ``(first, second)`` lies in its object's relation.

    Membership is asked of the represented relation subobject itself.  This keeps
    predicate-defined infinite relations nonenumerative and preserves an undecided
    membership proposition when their predicate is undecided.
    """
    relation_object = first.parent()
    if second.parent() is not relation_object:
        return False
    relation = relation_object.relation()
    ambient = relation.arrow().codomain()
    selected = relation.arrow().domain()
    pair = ambient.point((first.datum(), second.datum()))
    decision = sympy_ask(selected.membership_proposition(pair), assumptions)
    return None if decision is None else bool(decision)


def _decide_partial_order(
    relation_object: BinaryRelationsCategory.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    """Reflexivity, antisymmetry, and transitivity of a finite relation (Mathlib ``PartialOrder``)."""
    carrier = relation_object.carrier()
    data = tuple(point.datum() for point in carrier)
    pairs = _related_pairs(relation_object)
    reflexive = all((value, value) in pairs for value in data)
    antisymmetric = all(first == second for first in data for second in data if (first, second) in pairs and (second, first) in pairs)
    transitive = all((first, third) in pairs for first in data for second in data for third in data if (first, second) in pairs and (second, third) in pairs)
    return reflexive and antisymmetric and transitive


class BinaryRelationsCategory(Category[[MorphismCategory.ObjectType], []]):
    """Sets equipped with a binary endorelation, and relation-preserving maps."""

    _forgetful: Functor | None = None

    class ObjectType:
        def __init__(self, relation: CategoryOfCategories.ElementType) -> None:
            self._relation = relation
            self._carrier = _square_factor(relation.arrow().codomain())

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

    def _equal_morphisms(
        self,
        first: BinaryRelationsCategory.MorphismType,
        second: BinaryRelationsCategory.MorphismType,
        assumptions: Proposition,
    ) -> bool | None:
        """``to_sets()`` is faithful: equal endpoints and one underlying set map make one morphism."""
        if first.domain() is not second.domain() or first.codomain() is not second.codomain():
            return False
        return sympy_ask(first.underlying_map() == second.underlying_map(), assumptions)

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

    def lift_order(
        self,
        diagram: Functor,
        presentation: LimitConesCategory.ObjectType,
    ) -> BinaryRelationsCategory.ObjectType:
        """The componentwise order on the selected set-limit apex: ``x <= y`` iff every leg compares."""
        shape = diagram.domain()
        vertices = tuple(shape(label) for label in shape.labels())

        def componentwise(
            first: CategoryOfCategories.ElementType,
            second: CategoryOfCategories.ElementType,
        ) -> Proposition:
            def compares(vertex: CategoryOfCategories.ElementType) -> Proposition:
                factor, leg = diagram.on_object(vertex), presentation.leg(vertex)
                return factor.related(factor.point(leg(first).datum()), factor.point(leg(second).datum()))

            return conjunction(compares(vertex) for vertex in vertices)

        return self.from_predicate(presentation.apex(), componentwise)

    def transport(
        self,
        relation_object: BinaryRelationsCategory.ObjectType,
        bijection: MorphismCategory.ObjectType,
    ) -> BinaryRelationsCategory.MorphismType:
        """Transport a relation along a retained set isomorphism (D183).

        The inverse is supplied by the isomorphism itself.  No carrier is enumerated:
        ``y S y'`` is defined by ``f^-1(y) R f^-1(y')`` pointwise, so this works equally
        for finite, infinite and predicate-defined carriers.
        """
        carrier = relation_object.carrier()
        assert bijection.domain() is carrier, f"{bijection!r} does not start at the carrier of {relation_object!r}"
        inverse = bijection.inverse()
        image = bijection.codomain()
        assert inverse.domain() is image and inverse.codomain() is carrier

        def transported_rule(
            first: CategoryOfCategories.ElementType,
            second: CategoryOfCategories.ElementType,
        ) -> Proposition:
            return relation_object.related(
                relation_object.point(inverse(first).datum()),
                relation_object.point(inverse(second).datum()),
            )

        transported = self.from_predicate(image, transported_rule)
        # Preservation in both directions is the defining equation above, so this
        # theorem-backed lift must not re-enumerate the source relation merely to
        # rediscover it pointwise.
        forward = self.MorphismType(domain=relation_object, codomain=transported, data=bijection)
        backward = self.MorphismType(domain=transported, codomain=relation_object, data=inverse)
        self.retain_inverses(forward, backward)
        return forward

    def to_sets(self) -> Functor:
        """The faithful isofibration ``(X, R) |-> X`` forgetting the relation (D163).

        It carries the chosen lift of a discrete set limit: the componentwise order on
        the selected set apex (D183, ``specs/ordered-sets.md``, "Products").
        """
        if self._forgetful is None:
            self._forgetful = (
                Fun(self, Sets)
                .Faithful()
                .Isofibrations()(
                    lambda relation_object: relation_object._carrier,
                    lambda arrow: arrow._underlying_map,
                )
                .with_limit_lifting(Discrete, self.lift_order, self.construct_morphism)
            )
        return self._forgetful

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
        assert all((images[first], images[second]) in target_pairs for first, second in _related_pairs(source)), f"{underlying!r} does not preserve the relation of {source!r}"
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
register_handler(BinaryRelations().equality(), BinaryRelations()._equal_morphisms)


def _thin_category(poset_object: BinaryRelationsCategory.ObjectType) -> ThinCategory:
    """The thin category of a poset: its points, one arrow ``x -> y`` exactly when ``x <= y``."""
    return ThinCategory(poset_object, order_related)


def _thin_functor(monotone: BinaryRelationsCategory.MorphismType) -> Functor:
    """The functor a monotone map induces: a point to its image, a comparison to the compared images."""
    source, target = Thin.on_object(monotone.domain()), Thin.on_object(monotone.codomain())

    def on_object(member_object: ThinCategory.ObjectType) -> ThinCategory.ObjectType:
        return target(monotone(member_object.point()))

    def on_morphism(comparison: ThinCategory.MorphismType) -> ThinCategory.MorphismType:
        return Mor(target)(on_object(comparison.domain()), on_object(comparison.codomain()))()

    return Fun(source, target)(on_object, on_morphism)


Thin: Functor = Fun(Posets(), Cat())(_thin_category, _thin_functor)
