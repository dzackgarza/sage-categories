"""Finite posets."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, TypeIs

from sage_categories.abstract_categories.category_constructions import (
    FullSubcategory,
    FullSubcategoryArrow,
    FullSubcategoryElement,
    FullSubcategoryObject,
)
from sage_categories.abstract_categories.functors import (
    InclusionFunctor,
    StructuralFunctor,
)
from sage_categories.theories.sets import (
    FiniteSets,
    SetObject,
)
from sage_categories.values import (
    MathematicalObject,
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

    _sage_poset_constructor: ExternalPosetConstructor
else:
    from sage.combinat.posets.posets import Poset as _sage_poset_constructor


class FinitePosetObject(FullSubcategoryObject):
    """A finite poset with finite order algorithms."""

    _sage_value: ExternalFinitePoset | None = None

    def _sage_poset(self) -> ExternalFinitePoset:
        if self._sage_value is None:
            members = tuple(self)

            def relation(left: PosetElement, right: PosetElement) -> bool:
                comparison = left <= right
                assert isinstance(comparison, bool)
                return comparison

            self._sage_value = _sage_poset_constructor(
                (members, relation),
                facade=True,
            )
        return self._sage_value

    def covers(
        self,
        lower: PosetElement,
        upper: PosetElement,
    ) -> bool:
        return self._sage_poset().covers(lower, upper)

    def lower_covers(self, member: PosetElement) -> Iterator[PosetElement]:
        return iter(self._sage_poset().lower_covers(member))

    def upper_covers(self, member: PosetElement) -> Iterator[PosetElement]:
        return iter(self._sage_poset().upper_covers(member))

    def common_lower_covers(
        self,
        members: Iterable[PosetElement],
    ) -> Iterator[PosetElement]:
        return iter(self._sage_poset().common_lower_covers(tuple(members)))

    def common_upper_covers(
        self,
        members: Iterable[PosetElement],
    ) -> Iterator[PosetElement]:
        return iter(self._sage_poset().common_upper_covers(tuple(members)))

    def open_interval(
        self,
        lower: PosetElement,
        upper: PosetElement,
    ) -> Iterator[PosetElement]:
        return iter(self._sage_poset().open_interval(lower, upper))

    def closed_interval(
        self,
        lower: PosetElement,
        upper: PosetElement,
    ) -> Iterator[PosetElement]:
        return iter(self._sage_poset().closed_interval(lower, upper))

    def principal_order_ideal(
        self,
        member: PosetElement,
    ) -> Iterator[PosetElement]:
        return self.order_ideal((member,))

    def principal_order_filter(
        self,
        member: PosetElement,
    ) -> Iterator[PosetElement]:
        return self.order_filter((member,))

    def order_ideal(
        self,
        members: Iterable[PosetElement],
    ) -> Iterator[PosetElement]:
        return iter(self._sage_poset().order_ideal(tuple(members)))

    def order_filter(
        self,
        members: Iterable[PosetElement],
    ) -> Iterator[PosetElement]:
        return iter(self._sage_poset().order_filter(tuple(members)))

    def minimal_elements(self) -> Iterator[PosetElement]:
        return iter(self._sage_poset().minimal_elements())

    def maximal_elements(self) -> Iterator[PosetElement]:
        return iter(self._sage_poset().maximal_elements())

    def has_bottom(self) -> bool:
        return self._sage_poset().has_bottom()

    def bottom(self) -> PosetElement:
        assert self.has_bottom()
        return self._sage_poset().bottom()

    def has_top(self) -> bool:
        return self._sage_poset().has_top()

    def top(self) -> PosetElement:
        assert self.has_top()
        return self._sage_poset().top()

    def is_bounded(self) -> bool:
        return self._sage_poset().is_bounded()

    def height(self) -> int:
        return int(self._sage_poset().height())

    def width(self) -> int:
        return int(self._sage_poset().width())

    def rank(self, member: PosetElement | None = None) -> int:
        return int(self._sage_poset().rank(member))

    def level_sets(self) -> Iterator[Iterator[PosetElement]]:
        return iter(iter(level) for level in self._sage_poset().level_sets())

    def is_ranked(self) -> bool:
        return self._sage_poset().is_ranked()

    def is_graded(self) -> bool:
        return self._sage_poset().is_graded()

    def is_chain(self) -> bool:
        return self._sage_poset().is_chain()

    def is_chain_of_poset(self, members: Iterable[PosetElement]) -> bool:
        return self._sage_poset().is_chain_of_poset(tuple(members))

    def is_antichain_of_poset(self, members: Iterable[PosetElement]) -> bool:
        return self._sage_poset().is_antichain_of_poset(tuple(members))

    def linear_extension(self) -> Iterator[PosetElement]:
        return iter(self._sage_poset().linear_extension())


class FinitePosetElement(FullSubcategoryElement):
    """An element of one finite poset."""


class FinitePosetMorphism(FullSubcategoryArrow):
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
        value = self.refine_from_theorem(poset)
        assert self.contains_finite_poset(value)
        return value

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
