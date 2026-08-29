"""Minimal predicate-backed leaf for ``PartiallyOrderedSets()``.

This file is design pseudocode (``POL-LEAF-014``). Its identifiers show the
required contract. They do not define a second framework API.

The default public call accepts an owned relation subobject ``R -> X * X``.
The property-category constructor refines that same relation after the partial-order
laws are established. A named convenience constructor accepts an owned set and an
order rule, then constructs the relation first. The retained projection to ``X`` is
the only structure functor.
"""

from __future__ import annotations


class PartiallyOrderedSetsCategory(PredicateSubcategory):
    """The category of partially ordered sets and monotone maps."""

    _base_category_class_and_axiom = (
        BinaryRelationsCategory,
        "PartialOrder",
    )

    class ObjectType:
        """Add only operations guaranteed by the partial-order laws."""

        def order_relation(self) -> BinaryRelationSubobject:
            """Return the defining subobject of ``X * X``."""
            return self.relation_subobject()

    class ElementType:
        """Add order comparison to points of a poset."""

        def __le__(
            self,
            other: "PartiallyOrderedSets().ElementType",
        ) -> Proposition:
            """Return the proposition ``self <= other``."""
            assert other.parent() is self.parent()
            return self.parent().order_relation().contains_pair(self, other)

    class MorphismType:
        """Implement monotone maps."""

    def _predicate(
        self,
        relation: BinaryRelationSubobject,
    ) -> Proposition:
        """Return the conjunction of the three partial-order laws."""
        return (
            Reflexive(relation)
            & Antisymmetric(relation)
            & Transitive(relation)
        )

    def from_rule(
        self,
        X: Sets().ObjectType,
        order_rule: OrderRule,
    ) -> "PartiallyOrderedSets().ObjectType":
        """Construct the relation subobject selected by ``order_rule`` first."""
        product = Sets().Products()((X, X))
        relation = Sets().MonoOver(product).from_predicate(order_rule)
        return self(relation)

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Select the set projection for inherited set operations."""
        return (self.product_projection(0),)
