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
    FiniteSet,
    FiniteSets,
    PowerSet,
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


class FinitePosetObject(TransportedObject):
    """A finite poset with finite order algorithms."""

    _sage_value: ExternalFinitePoset | None = None

    def _sage_poset(self) -> ExternalFinitePoset:
        if self._sage_value is None:
            members = tuple(self)

            def relation(left: PosetElement, right: PosetElement) -> bool:
                comparison = left <= right
                assert comparison is True or comparison is False
                return comparison

            self._sage_value = _sage_poset_constructor(
                (members, relation),
                facade=True,
            )
        return self._sage_value

    def _underlying_set(self) -> SetObject:
        return PartiallyOrderedSets().underlying_set(self)

    def _sage_element(self, member: PosetElement) -> PosetElement:
        assert member in self
        return member

    def _owned_element(self, member: PosetElement) -> PosetElement:
        assert member in self
        return self.element(member._set_implementation())

    def _owned_subset(self, members: Iterable[PosetElement]) -> SetSubset:
        owned = frozenset(
            self._owned_element(member)._set_implementation()
            for member in members
        )
        return PowerSet(self._underlying_set()).from_finite_set(FiniteSet(owned))

    def _sage_members(self, members: SetSubset) -> tuple[PosetElement, ...]:
        assert members.base_set() is self._underlying_set()
        inclusion = members.inclusion()
        return tuple(
            self.element(inclusion(member))
            for member in members.underlying_set()
        )

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

    def has_bottom(self) -> bool:
        return self._sage_poset().has_bottom()

    def bottom(self) -> PosetElement:
        assert self.has_bottom()
        return self._owned_element(self._sage_poset().bottom())

    def has_top(self) -> bool:
        return self._sage_poset().has_top()

    def top(self) -> PosetElement:
        assert self.has_top()
        return self._owned_element(self._sage_poset().top())

    def is_bounded(self) -> bool:
        return self._sage_poset().is_bounded()

    def height(self) -> Cardinal:
        return cardinal(int(self._sage_poset().height()))

    def width(self) -> Cardinal:
        return cardinal(int(self._sage_poset().width()))

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

    def is_ranked(self) -> bool:
        return self._sage_poset().is_ranked()

    def is_graded(self) -> bool:
        return self._sage_poset().is_graded()

    def is_chain(self) -> bool:
        return self._sage_poset().is_chain()

    def is_chain_of_poset(self, members: SetSubset) -> bool:
        return self._sage_poset().is_chain_of_poset(self._sage_members(members))

    def is_antichain_of_poset(self, members: SetSubset) -> bool:
        return self._sage_poset().is_antichain_of_poset(self._sage_members(members))

    def linear_extension(self) -> FiniteTotalOrderObject:
        from sage_categories.theories.ordered_set_constructors import (
            ordered_set_owned_by,
        )

        elements = tuple(
            self._owned_element(member)._set_implementation()
            for member in self._sage_poset().linear_extension()
        )
        result = ordered_set_owned_by(elements)
        from sage_categories.theories.total_orders import FiniteTotallyOrderedSets

        assert FiniteTotallyOrderedSets().contains_finite_total_order(result)
        return result


class FinitePosetElement(TransportedElement):
    """An element of one finite poset."""


class FinitePosetMorphism(TransportedArrow):
    """An order-preserving map between finite posets."""


class FinitePosetsCategory(FullSubcategory):
    """The full subcategory of finite partially ordered sets."""

    ObjectType: type[FinitePosetObject] = FinitePosetObject
    ElementType: type[FinitePosetElement] = FinitePosetElement
    ArrowType: type[FinitePosetMorphism] = FinitePosetMorphism

    def __init__(self, posets: PartiallyOrderedSetsCategory) -> None:
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

    def __repr__(self) -> str:
        return "Finite partially ordered sets"
