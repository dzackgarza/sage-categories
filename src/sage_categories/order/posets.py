"""Sets equipped with a binary relation, and their partial-order subcategory.

An object of ``BinaryRelations()`` is a set ``X`` together with the data of a
relation ``R <= X * X`` (Mathlib ``CategoryTheory`` relation objects; a poset is a
set with such data, not a relation).  Its structure functor to ``Sets()`` forgets the
relation, so a relation object inherits point, map, and set behavior from its carrier.
``Posets()`` is the ``PartialOrder`` property subcategory of ``BinaryRelations()``.
"""

from __future__ import annotations

__all__ = [
    "BinaryRelations",
    "BinaryRelationsCategory",
    "FinitePosets",
    "FinitePosetsCategory",
    "FiniteTotallyOrderedSets",
    "Posets",
    "PosetsCategory",
    "Thin",
    "TotallyOrderedSets",
    "order_preserving",
]

from collections.abc import Callable

from sympy import ask as sympy_ask
from sympy.logic.boolalg import Boolean

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Cat, Fun, Functor
from sage_categories.cat.leaf_categories import FaithfulStructureCategory
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
from sage_categories.order._firewall import finite_posets as _finite_posets_firewall
from sage_categories.sets.finite import SetsCategory

type OrderRule = Callable[[CategoryOfCategories.ElementType, CategoryOfCategories.ElementType], Proposition]


class _OrderRelatedPredicate(Predicate):
    name = "order_related"


class _PartialOrderPredicate(Predicate):
    name = "partial_order"


class _TotalOrderPredicate(Predicate):
    name = "total_order"


class _OrderPreservingPredicate(Predicate):
    name = "order_preserving"


order_related = _OrderRelatedPredicate()
partial_order = _PartialOrderPredicate()
total_order = _TotalOrderPredicate()
order_preserving = _OrderPreservingPredicate()


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
    return _finite_posets_firewall.partial_order(relation_object)


class BinaryRelationsCategory(FaithfulStructureCategory):
    """Sets equipped with a binary endorelation, and relation-preserving maps."""

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
        # named transport must not re-enumerate the source relation merely to
        # rediscover it pointwise.
        forward = self._morphism_from_data(relation_object, transported, bijection)
        backward = self._morphism_from_data(transported, relation_object, inverse)
        self.retain_inverses(forward, backward)
        return forward

    def to_sets(self) -> Functor:
        """The faithful isofibration ``(X, R) |-> X`` forgetting the relation (D163).

        It carries the chosen lift of a discrete set limit: the componentwise order on
        the selected set apex (D183, ``specs/ordered-sets.md``, "Products").
        """
        return next(functor for functor in self.selected_functors() if functor.codomain() is Sets)

    def structure_functors(self) -> tuple[Functor, ...]:
        underlying = (
            Fun(self, Sets)
            .Faithful()
            .Isofibrations()(
                lambda relation_object: relation_object.carrier(),
                lambda arrow: arrow.underlying_map(),
            )
            .with_limit_lifting(Discrete, self.lift_order, self.construct_morphism)
        )
        return (underlying,)

    def construct_morphism(
        self,
        source: BinaryRelationsCategory.ObjectType,
        target: BinaryRelationsCategory.ObjectType,
        underlying: MorphismCategory.ObjectType,
    ) -> BinaryRelationsCategory.MorphismType:
        source_carrier, target_carrier = source.carrier(), target.carrier()
        assert underlying.domain() is source_carrier and underlying.codomain() is target_carrier
        assert sympy_ask(order_preserving(source, target, underlying)) is True, (
            f"{underlying!r} is not established to preserve the relation of {source!r}"
        )
        return self._morphism_from_data(source, target, underlying)


class PosetsCategory(PropertySubcategory):
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

    def to_sets(self) -> Functor:
        """The underlying-set functor ``U: Posets() -> Sets()``.

        ``Posets()`` is the full partial-order subcategory of ``BinaryRelations()``;
        restricting the relation projection is therefore the one owned underlying-set
        functor, with no second object or morphism action in the poset leaf.
        """
        return BinaryRelations().to_sets().restrict(self, Sets)

    Finite = SetsCategory.Finite.inverse_image(lambda category: category.to_sets())


class FinitePosetsCategory(Category):
    """The implementation surface of the exact derived category ``Posets().Finite()``.

    The category itself is the inverse image selected by ``PosetsCategory.Finite``.
    This implementation claims that exact value in place so finite-poset operations can
    live on its three ordinary roles without constructing a second property category.
    """

    class ObjectType:
        """A finite poset; finite algorithms are owned by this role."""

    class ElementType:
        """An element inherited from the ambient poset."""

    class MorphismType:
        """A monotone map between finite posets."""

    def structure_functors(self) -> tuple[Functor, ...]:
        finite_posets = FinitePosets()
        return (Fun(finite_posets, finite_posets).one(),)


_BINARY_RELATIONS = BinaryRelationsCategory()


def BinaryRelations() -> BinaryRelationsCategory:
    """The category of sets equipped with a binary relation."""
    return _BINARY_RELATIONS


def Posets() -> Category:
    """The category of partial orders: ``BinaryRelations().PartialOrder()``."""
    return BinaryRelations().PartialOrder()


def TotallyOrderedSets() -> Category:
    """The category of total orders: ``Posets().Total()``."""
    return Posets().Total()


def FinitePosets() -> FinitePosetsCategory:
    """Finite posets: ``U.inverse_image(Sets().Finite())`` for ``U: Posets() -> Sets()``."""
    return Posets().Finite()


def FiniteTotallyOrderedSets() -> Category:
    """Finite total orders: the finite inverse image along ``TotallyOrderedSets() -> Posets()``."""
    return TotallyOrderedSets().Finite()


def _decide_total_order(
    poset_object: BinaryRelationsCategory.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    """Totality of a finite order through Sage's finite-poset implementation."""
    return _finite_posets_firewall.total_order(poset_object)


def _decide_order_preserving(
    source: BinaryRelationsCategory.ObjectType,
    target: BinaryRelationsCategory.ObjectType,
    underlying: MorphismCategory.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    """Exact finite monotonicity, delegated to the private finite-order boundary."""
    return _finite_posets_firewall.order_preserving(source, target, underlying, assumptions)


register_handler(order_related, _decide_order_related)
register_handler(partial_order, _decide_partial_order)
register_handler(total_order, _decide_total_order)
register_handler(order_preserving, _decide_order_preserving)
register_handler(BinaryRelations().equality(), BinaryRelations()._equal_morphisms)
Cat().implement(FinitePosetsCategory)


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
