"""Local declarations for a ``PartiallyOrderedSets()`` specimen.

This design pseudocode constructs a poset from its relation subobject.
It also supplies the local projection to ``Sets()``.
See ``leaves.md`` and ``functor.md`` for the governing contracts.
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
        relation = Sets().Subobjects(product).from_predicate(order_rule)
        return self(relation)

    def sets_projection(self) -> Cat().MorphismType:
        """Return the named functor from posets to their sets of points."""
        target_category = Sets()

        def on_object(
            P: "PartiallyOrderedSets().ObjectType",
        ) -> Sets().ObjectType:
            product = P.order_relation().ambient_object()
            points = product.product_projection(0).codomain()
            return target_category(points)

        def on_morphism(
            f: "PartiallyOrderedSets().MorphismType",
        ) -> Sets().MorphismType:
            source = on_object(f.domain())
            target = on_object(f.codomain())
            return Mor(target_category)(source, target)(lambda x: f(x))

        return Fun(self, target_category)(on_object, on_morphism)

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Select the set projection for inherited set operations."""
        return (self.sets_projection(),)
