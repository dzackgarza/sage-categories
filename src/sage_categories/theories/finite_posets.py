"""Finite posets."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, TypeIs

from sage_categories.abstract_categories.category_constructions import (
    FullSubcategory,
)
from sage_categories.abstract_categories.functors import (
    InclusionFunctor,
    StructuralFunctor,
)
from sage_categories.theories.sets import (
    DiscreteCategory,
    EnumerationInjection,
    FiniteSet,
    FiniteSets,
    PowerSet,
    SetElement,
    SetObject,
    SetSubset,
    SubsetsOfSet,
)
from sage_categories.theories.cardinals import Cardinal, cardinal
from sage_categories.abstract_categories.functors import DiscreteDiagram
from sage_categories.values import (
    MathematicalObject,
    TransportedArrow,
    TransportedElement,
    TransportedObject,
)

from sage_categories.theories.poset_core import (
    OrderRelation,
    PartiallyOrderedSets,
    PartiallyOrderedSetsCategory,
    PosetElement,
    PosetObject,
)

if TYPE_CHECKING:
    from sage_categories.backends.sage._finite_posets_types import (
        ExternalFinitePoset,
        ExternalPosetConstructor,
    )
    from sage_categories.theories.total_orders import FiniteTotalOrderObject

    _sage_poset_constructor: ExternalPosetConstructor
else:
    from sage.combinat.posets.posets import Poset as _sage_poset_constructor


class _FinitePosetSageBoundary:
    """Private lowering and reconstruction for Sage finite-poset algorithms."""

    _sage_value: ExternalFinitePoset | None = None

    def _sage_poset(self) -> ExternalFinitePoset:
        if self._sage_value is None:
            members = tuple(self._underlying_set())

            def relation(left: SetElement, right: SetElement) -> bool:
                comparison = self.element(left) <= self.element(right)
                assert comparison is True or comparison is False
                return comparison

            self._sage_value = _sage_poset_constructor(
                (members, relation),
                facade=True,
            )
        return self._sage_value

    def _underlying_set(self) -> SetObject:
        return PartiallyOrderedSets().underlying_set(self)

    def _sage_element(self, member: PosetElement) -> SetElement:
        assert member in self
        image = member._set_implementation()
        assert image.ambient_set() is self._underlying_set()
        return image

    def _owned_element(self, member: SetElement) -> PosetElement:
        assert member.ambient_set() is self._underlying_set()
        return self.element(member)

    def _owned_subset(self, members: Iterable[SetElement]) -> SetSubset:
        owned = frozenset(
            self._owned_element(member)._set_implementation()
            for member in members
        )
        return PowerSet(self._underlying_set()).from_finite_set(FiniteSet(owned))

    def _sage_members(self, members: SetSubset) -> tuple[SetElement, ...]:
        assert members.base_set() is self._underlying_set()
        inclusion = members.inclusion()
        return tuple(
            inclusion(member)
            for member in members.underlying_set()
        )


class FinitePosetObject(_FinitePosetSageBoundary, TransportedObject):
    """A finite poset with finite order algorithms."""

    def covers(
        self,
        lower: PosetElement,
        upper: PosetElement,
    ) -> bool:
        return self._sage_poset().covers(
            self._sage_element(lower),
            self._sage_element(upper),
        )

    def lower_covers(self, member: PosetElement) -> SetSubset:
        return self._owned_subset(
            self._sage_poset().lower_covers(self._sage_element(member)),
        )

    def upper_covers(self, member: PosetElement) -> SetSubset:
        return self._owned_subset(
            self._sage_poset().upper_covers(self._sage_element(member)),
        )

    def common_lower_covers(
        self,
        members: SetSubset,
    ) -> SetSubset:
        return self._owned_subset(
            self._sage_poset().common_lower_covers(self._sage_members(members)),
        )

    def common_upper_covers(
        self,
        members: SetSubset,
    ) -> SetSubset:
        return self._owned_subset(
            self._sage_poset().common_upper_covers(self._sage_members(members)),
        )

    def open_interval(
        self,
        lower: PosetElement,
        upper: PosetElement,
    ) -> SetSubset:
        return self._owned_subset(
            self._sage_poset().open_interval(
                self._sage_element(lower),
                self._sage_element(upper),
            ),
        )

    def closed_interval(
        self,
        lower: PosetElement,
        upper: PosetElement,
    ) -> SetSubset:
        return self._owned_subset(
            self._sage_poset().closed_interval(
                self._sage_element(lower),
                self._sage_element(upper),
            ),
        )

    def principal_order_ideal(
        self,
        member: PosetElement,
    ) -> SetSubset:
        singleton = PowerSet(self._underlying_set()).from_finite_set(
            FiniteSet((member._set_implementation(),)),
        )
        return self.order_ideal(singleton)

    def principal_order_filter(
        self,
        member: PosetElement,
    ) -> SetSubset:
        singleton = PowerSet(self._underlying_set()).from_finite_set(
            FiniteSet((member._set_implementation(),)),
        )
        return self.order_filter(singleton)

    def order_ideal(
        self,
        members: SetSubset,
    ) -> SetSubset:
        return self._owned_subset(
            self._sage_poset().order_ideal(self._sage_members(members)),
        )

    def order_filter(
        self,
        members: SetSubset,
    ) -> SetSubset:
        return self._owned_subset(
            self._sage_poset().order_filter(self._sage_members(members)),
        )

    def minimal_elements(self) -> SetSubset:
        return self._owned_subset(self._sage_poset().minimal_elements())

    def maximal_elements(self) -> SetSubset:
        return self._owned_subset(self._sage_poset().maximal_elements())

    def height(self) -> Cardinal:
        return cardinal(int(self._sage_poset().height()))

    def width(self) -> Cardinal:
        return cardinal(int(self._sage_poset().width()))

    def is_chain(self) -> bool:
        return self._sage_poset().is_chain()

    def is_chain_of_poset(self, members: SetSubset) -> bool:
        return self._sage_poset().is_chain_of_poset(self._sage_members(members))

    def is_antichain_of_poset(self, members: SetSubset) -> bool:
        return self._sage_poset().is_antichain_of_poset(self._sage_members(members))

    def linear_extension(self) -> FiniteTotalOrderObject:
        elements = tuple(self._sage_poset().linear_extension())
        positions = {
            member: position
            for position, member in enumerate(elements)
        }
        enumeration = EnumerationInjection(
            self._underlying_set(),
            lambda member: positions[member],
        )
        from sage_categories.theories.total_orders import FiniteTotallyOrderedSets

        result = FiniteTotallyOrderedSets().from_enumeration(enumeration)
        assert FiniteTotallyOrderedSets().contains_finite_total_order(result)
        return result


class FinitePosetElement(TransportedElement):
    """An element of one finite poset."""


class FinitePosetMorphism(TransportedArrow):
    """An order-preserving map between finite posets."""


class FinitePosetWithBottomObject(_FinitePosetSageBoundary, TransportedObject):
    """A finite poset with a least element."""

    def bottom(self) -> PosetElement:
        return self._owned_element(self._sage_poset().bottom())


class FinitePosetWithTopObject(_FinitePosetSageBoundary, TransportedObject):
    """A finite poset with a greatest element."""

    def top(self) -> PosetElement:
        return self._owned_element(self._sage_poset().top())


class RankedFinitePosetObject(_FinitePosetSageBoundary, TransportedObject):
    """A ranked finite poset."""

    def rank(self) -> Cardinal:
        return cardinal(int(self._sage_poset().rank()))

    def rank_of_element(self, member: PosetElement) -> Cardinal:
        return cardinal(int(self._sage_poset().rank(self._sage_element(member))))

    def level_sets(self) -> DiscreteDiagram:
        from sage_categories.theories.ordinals import Ordinal, ordinal

        levels = tuple(
            self._owned_subset(level)
            for level in self._sage_poset().level_sets()
        )
        labels = FiniteSet(ordinal(index) for index in range(len(levels)))
        index = DiscreteCategory(labels)
        level_by_index: dict[Ordinal, SetSubset] = {
            ordinal(position): level
            for position, level in enumerate(levels)
        }
        return DiscreteDiagram(
            index,
            SubsetsOfSet(self._underlying_set()),
            lambda source: level_by_index[source.label().value()],
        )


class GradedFinitePosetObject(_FinitePosetSageBoundary, TransportedObject):
    """A graded finite poset."""


class FinitePosetWithBottomElement(TransportedElement):
    """An element of a finite poset with a least element."""


class FinitePosetWithTopElement(TransportedElement):
    """An element of a finite poset with a greatest element."""


class RankedFinitePosetElement(TransportedElement):
    """An element of a ranked finite poset."""


class GradedFinitePosetElement(TransportedElement):
    """An element of a graded finite poset."""


class FinitePosetWithBottomMorphism(TransportedArrow):
    """A morphism between finite posets with least elements."""


class FinitePosetWithTopMorphism(TransportedArrow):
    """A morphism between finite posets with greatest elements."""


class RankedFinitePosetMorphism(TransportedArrow):
    """A morphism between ranked finite posets."""


class GradedFinitePosetMorphism(TransportedArrow):
    """A morphism between graded finite posets."""


class FinitePosetsCategory(FullSubcategory):
    """The full subcategory of finite partially ordered sets."""

    ObjectType: type[FinitePosetObject] = FinitePosetObject
    ElementType: type[FinitePosetElement] = FinitePosetElement
    ArrowType: type[FinitePosetMorphism] = FinitePosetMorphism

    def __init__(self, posets: PartiallyOrderedSetsCategory) -> None:
        self._with_bottom: FinitePosetsWithBottomCategory | None = None
        self._with_top: FinitePosetsWithTopCategory | None = None
        self._ranked: RankedFinitePosetsCategory | None = None
        self._graded: GradedFinitePosetsCategory | None = None
        super().__init__(
            posets,
            self._is_finite,
            name="Finite partially ordered sets",
        )

    def __call__(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> FinitePosetObject:
        assert underlying_set in FiniteSets()
        poset = PartiallyOrderedSets()(underlying_set, relation)
        assert self.contains_finite_poset(poset)
        return poset

    def from_finite_underlying_poset(
        self,
        poset: PosetObject,
    ) -> FinitePosetObject:
        underlying_set = PartiallyOrderedSets().underlying_set(poset)
        assert underlying_set in FiniteSets()
        result = self._refine_object(poset)
        assert self.contains_finite_poset(result)
        return result

    def _is_finite(self, value: MathematicalObject) -> bool:
        assert PartiallyOrderedSets().contains_poset(value)
        return PartiallyOrderedSets().underlying_set(value) in FiniteSets()

    def contains_finite_poset(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[FinitePosetObject]:
        return candidate in self

    def WithBottom(self) -> FinitePosetsWithBottomCategory:
        if self._with_bottom is None:
            self._with_bottom = FinitePosetsWithBottomCategory(self)
        return self._with_bottom

    def WithTop(self) -> FinitePosetsWithTopCategory:
        if self._with_top is None:
            self._with_top = FinitePosetsWithTopCategory(self)
        return self._with_top

    def Ranked(self) -> RankedFinitePosetsCategory:
        if self._ranked is None:
            self._ranked = RankedFinitePosetsCategory(self)
        return self._ranked

    def Graded(self) -> GradedFinitePosetsCategory:
        if self._graded is None:
            self._graded = GradedFinitePosetsCategory(self.Ranked())
        return self._graded

    def __repr__(self) -> str:
        return "Finite partially ordered sets"


class FinitePosetsWithBottomCategory(FullSubcategory):
    """Finite posets with a least element."""

    ObjectType = FinitePosetWithBottomObject
    ElementType = FinitePosetWithBottomElement
    ArrowType = FinitePosetWithBottomMorphism

    def __init__(self, finite_posets: FinitePosetsCategory) -> None:
        super().__init__(
            finite_posets,
            self._has_bottom,
            name="Finite posets with a least element",
        )

    def _has_bottom(self, value: MathematicalObject) -> bool:
        assert PartiallyOrderedSets().Finite().contains_finite_poset(value)
        return value._sage_poset().has_bottom()

    def contains_poset_with_bottom(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[FinitePosetWithBottomObject]:
        return candidate in self


class FinitePosetsWithTopCategory(FullSubcategory):
    """Finite posets with a greatest element."""

    ObjectType = FinitePosetWithTopObject
    ElementType = FinitePosetWithTopElement
    ArrowType = FinitePosetWithTopMorphism

    def __init__(self, finite_posets: FinitePosetsCategory) -> None:
        super().__init__(
            finite_posets,
            self._has_top,
            name="Finite posets with a greatest element",
        )

    def _has_top(self, value: MathematicalObject) -> bool:
        assert PartiallyOrderedSets().Finite().contains_finite_poset(value)
        return value._sage_poset().has_top()

    def contains_poset_with_top(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[FinitePosetWithTopObject]:
        return candidate in self


class RankedFinitePosetsCategory(FullSubcategory):
    """Ranked finite posets."""

    ObjectType = RankedFinitePosetObject
    ElementType = RankedFinitePosetElement
    ArrowType = RankedFinitePosetMorphism

    def __init__(self, finite_posets: FinitePosetsCategory) -> None:
        super().__init__(
            finite_posets,
            self._is_ranked,
            name="Ranked finite posets",
        )

    def _is_ranked(self, value: MathematicalObject) -> bool:
        assert PartiallyOrderedSets().Finite().contains_finite_poset(value)
        return value._sage_poset().is_ranked()

    def contains_ranked_poset(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[RankedFinitePosetObject]:
        return candidate in self


class GradedFinitePosetsCategory(FullSubcategory):
    """Graded finite posets."""

    ObjectType = GradedFinitePosetObject
    ElementType = GradedFinitePosetElement
    ArrowType = GradedFinitePosetMorphism

    def __init__(self, ranked_posets: RankedFinitePosetsCategory) -> None:
        super().__init__(
            ranked_posets,
            self._is_graded,
            name="Graded finite posets",
        )

    def _is_graded(self, value: MathematicalObject) -> bool:
        assert PartiallyOrderedSets().Finite().Ranked().contains_ranked_poset(value)
        return value._sage_poset().is_graded()

    def contains_graded_poset(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[GradedFinitePosetObject]:
        return candidate in self
