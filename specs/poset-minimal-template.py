"""Minimal structured leaf for ``PartiallyOrderedSets()``.

A poset object is a pair ``(X, R)``. The constructor accepts only the owned
relation ``R``. Its ambient product determines ``X``.

The local object datum is ``R``. The selected set projection derives ``X`` from
the two equal factors of ``R``. It supplies the inherited set surface and the set
construction input. The relation remains the order data.

Both component projections are mathematical functors. Only the set projection
is a structure functor. The relation projection remains an ordinary functor because
its subset-of-a-product catalogue is not a public poset surface.

The poset category is a subcategory of a product category. The first factor contains
``X``. The second contains the relation subobject ``R``. The general
subobject-of-product construction supplies both component functors.

In particular, component zero is already an owned object of ``Sets()``. The projection
extracts that component and uses its canonical set image. No poset method delegates to
the component by hand.

Elements add no constructor data. The kernel constructs the exact
``PartiallyOrderedSets().ElementType`` with its ambient poset and retains its
canonical image in the projected set.

This example presents ``R`` as ``<=``. A strict-order presentation would own
the corresponding ``<`` operation instead.

Construction in ``PartiallyOrderedSets()`` asserts that ``R`` satisfies the partial-order
laws. The constructor does not run a law checker. A relation-bearing ambient object can
instead expose a property proposition and bind exact handlers through the property
subcategory template.

The ``ask()`` call below decides only the cardinality precondition used by this
construction. It does not decide the partial-order laws. Theory code constructs known
posets directly. Interactive code can use ``assume(proposition)`` or
``proposition.assume()`` for a property supplied by the mathematical context.
"""

from __future__ import annotations


SetRelation = Sets().Products().Subsets().ObjectType


@dataclass(frozen=True, slots=True)
class PosetObjectData:
    """The order data introduced by a partial order."""

    relation: SetRelation


@dataclass(frozen=True, slots=True)
class PosetMorphismData:
    """The construction datum consumed by the selected set functor."""

    set_map: SetMorphism


class PartiallyOrderedSetsCategory(Category):
    """The category of partially ordered sets and monotone maps."""

    class DeclaredObjectType(Implementation):
        """Implement the partial order determined by an owned relation."""

        def __init__(self, data: PosetObjectData) -> None:
            relation = data.relation
            assert relation in Sets().Products().Subsets()
            factors = relation.factors()
            assert ask(factors.cardinality() == 2) is True
            assert factors[1] is factors[0]
            self._relation = relation
            super().__init__()

        def order_relation(self) -> SetRelation:
            """Return the defining subobject of ``X × X``."""
            return self._relation

        def point(self, datum: Datum) -> PosetElement:
            """Construct the poset element over the inherited set point."""
            return self.element(super().point(datum))

        def element(self, point: SetElement) -> PosetElement:
            """Lift a canonical set point to the corresponding poset point."""
            posets = self.category()
            defining_morphism = Mor(posets)(posets.Terminal(), self)(
                PosetMorphismData(point.defining_morphism()),
            )
            return posets.element_from_defining_morphism(defining_morphism)

        def elements_are_related(
            self,
            left: PosetElement,
            right: PosetElement,
        ) -> Proposition:
            """Return the proposition that ``(left, right)`` belongs to ``R``."""
            assert left.ambient_object() is self
            assert right.ambient_object() is self
            return self.order_relation().contains_pair(left, right)

    class DeclaredElementType(Implementation):
        """Add order comparison to the inherited element implementation."""

        def __le__(
            self,
            other: PosetElement,
        ) -> Proposition:
            """Return the proposition that ``self <= other``."""
            return self.ambient_object().elements_are_related(self, other)

    class DeclaredMorphismType(Implementation):
        """Add no state beyond the map retained by the selected set functor."""

    def __call__(
        self,
        relation: SetRelation,
    ) -> Poset:
        """Construct the asserted partial order determined by ``relation``."""
        return self.ObjectType(
            category=self,
            data=PosetObjectData(relation),
        )

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Select the set projection used for inheritance."""
        # This tuple selects inheritance routes. It is not a list of all functors
        # from this category. Do not add the second product projection here.
        # A poset ``(X, R)`` receives its inherited public methods from ``X``.
        # Projection to ``R`` would expose subset and product methods on posets.
        # That projection can still exist and be called as an ordinary functor.
        # Selecting only ``X`` mirrors Sage listing only ``Sets()`` as a supercategory.
        # The product projection retains the object, element, and morphism data
        # conversions supplied by the general product construction.
        return (self.product_projection(0),)


_POSETS = PartiallyOrderedSetsCategory()
Poset = _POSETS.ObjectType
PosetElement = _POSETS.ElementType
MonotoneMap = _POSETS.MorphismType
