"""Minimal structured leaf for ``PartiallyOrderedSets()``.

A poset object is a pair ``(X, R)``. The constructor accepts only the owned
relation ``R``. Its ambient product determines ``X``.

The private defining data is ``(X, R)``. The kernel-owned carrier projection
selects component zero and supplies the inherited set surface. Component one
remains the order data.

Elements add no constructor data. The kernel constructs the exact
``PartiallyOrderedSets().ElementType`` with its ambient poset and retains its
canonical image in the projected set.

This example presents ``R`` as ``<=``. A strict-order presentation would own
the corresponding ``<`` operation instead.
"""

from __future__ import annotations


class PartiallyOrderedSetsCategory(Category):
    """The category of partially ordered sets and monotone maps."""

    class ObjectType(Implementation):
        """Implement the partial order determined by an owned relation."""

        def __init__(
            self,
            *,
            category: PartiallyOrderedSetsCategory,
            relation: SetSubset,
        ) -> None:
            assert relation in Sets().Products().Subsets()
            factors = relation.factors()
            assert factors.cardinality() == 2
            underlying_set = factors[0]
            assert factors[1] is underlying_set
            self._defining_data = (underlying_set, relation)
            super().__init__(category=category)

        def order_relation(self) -> SetSubset:
            """Return the defining subobject of ``X × X``."""
            return self._defining_data[1]

        def elements_are_related(
            self,
            left: PartiallyOrderedSetsCategory.ElementType,
            right: PartiallyOrderedSetsCategory.ElementType,
        ) -> Proposition:
            """Return the proposition that ``(left, right)`` belongs to ``R``."""
            assert left.ambient_object() is self
            assert right.ambient_object() is self
            return self.order_relation().contains_pair(left, right)

    class ElementType(Implementation):
        """Add order comparison to the inherited element implementation."""

        def __le__(
            self,
            other: PartiallyOrderedSetsCategory.ElementType,
        ) -> Proposition:
            """Return the proposition that ``self <= other``."""
            return self.ambient_object().elements_are_related(self, other)

    class ArrowType(Implementation):
        """Implement monotone maps with the inherited arrow surface."""

    def __call__(
        self,
        relation: SetSubset,
    ) -> PartiallyOrderedSetsCategory.ObjectType:
        """Construct the asserted partial order determined by ``relation``."""
        return self.ObjectType(category=self, relation=relation)

    def structure_functors(self) -> tuple[Functor, ...]:
        """Select the carrier projection used for inheritance."""
        carrier = ProductProjectionFunctor(0, self, Sets())
        return (carrier,)
