"""Local declarations for one ``Posets()`` design specimen.

This pseudocode constructs a poset from its relation subobject.
It also supplies the named projection to ``Sets()``.
"""

from __future__ import annotations

from sympy import ask
from sympy.assumptions import Predicate
from sympy.logic.boolalg import And, Boolean


class PartialOrderPredicate(Predicate):
    """State the partial-order laws for an owned binary relation."""

    name = "partial_order"


partial_order = PartialOrderPredicate()


class PosetsCategory(Category):
    """Implement posets and monotone maps."""

    _base_category_class_and_axiom = (
        BinaryRelationsCategory,
        "PartialOrder",
    )
    predicate = partial_order

    class ObjectType:
        """Add operations guaranteed by the partial-order laws."""

        def order_relation(self) -> BinaryRelationSubobject:
            """Return the defining subobject of ``X * X``."""
            return self.relation_subobject()

    class ElementType:
        """Add order comparison to points of a poset."""

        def __le__(self, other: Posets().ElementType) -> Boolean:
            """Return the proposition ``self <= other``."""
            assert other.parent() is self.parent()
            return self.parent().order_relation().contains_pair(self, other)

    class MorphismType:
        """Implement monotone maps."""

    def membership_proposition(
        self,
        relation: BinaryRelationSubobject,
    ) -> Boolean:
        """Apply the category-owned predicate without evaluation."""
        return partial_order(owned_value_atom(relation))

    def from_rule(
        self,
        X: Sets().ObjectType,
        order_rule: OrderRule,
    ) -> Posets().ObjectType:
        """Construct the relation subobject selected by ``order_rule``."""
        product = Sets().Products()((X, X))
        relation = Sets().Subobjects(product).from_predicate(order_rule)
        return self(relation)

    def sets_projection(self) -> Cat().MorphismType:
        """Return the named functor from posets to their sets of points."""
        target_category = Sets()

        def on_object(P: Posets().ObjectType) -> Sets().ObjectType:
            product = P.order_relation().ambient_object()
            points = product.product_projection(0).codomain()
            return target_category(points)

        def on_morphism(f: Posets().MorphismType) -> Sets().MorphismType:
            source = on_object(f.domain())
            target = on_object(f.codomain())
            return Mor(target_category)(source, target)(lambda x: f(x))

        return Fun(self, target_category)(on_object, on_morphism)

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Select the set projection for inherited set operations."""
        return (self.sets_projection(),)


@partial_order.register(OwnedValueAtom)
def decide_partial_order(
    relation: OwnedValueAtom,
    assumptions: Boolean,
) -> bool | None:
    """Ask exact handlers for the three partial-order laws."""
    owned_relation = relation.owned_value()
    result = And(
        Reflexive(owned_relation),
        Antisymmetric(owned_relation),
        Transitive(owned_relation),
    )
    return ask(result, assumptions)
