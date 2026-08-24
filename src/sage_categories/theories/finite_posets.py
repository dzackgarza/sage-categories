"""Finite posets."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, TypeIs

from sage_categories.abstract_categories.category_constructions import (
    FullSubcategory,
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

if TYPE_CHECKING:
    from sage_categories.backends.sage.finite_posets import (
        SageFinitePosetObject,
    )

from sage_categories.theories.poset_core import (
    OrderRelation,
    PartiallyOrderedSets,
    PartiallyOrderedSetsCategory,
    PosetElement,
    PosetObject,
)


class FinitePosetObject(FullSubcategoryObject):
    """A finite poset with finite order algorithms."""

    def _realization(self) -> SageFinitePosetObject:
        from sage_categories.backends.sage.finite_posets import (
            realize_finite_poset,
        )

        return realize_finite_poset(self)

    def covers(
        self,
        lower: PosetElement,
        upper: PosetElement,
    ) -> bool:
        return self._realization().covers(lower, upper)

    def lower_covers(self, member: PosetElement) -> Iterator[PosetElement]:
        return self._realization().lower_covers(member)

    def upper_covers(self, member: PosetElement) -> Iterator[PosetElement]:
        return self._realization().upper_covers(member)

    def common_lower_covers(
        self,
        members: Iterable[PosetElement],
    ) -> Iterator[PosetElement]:
        return self._realization().common_lower_covers(members)

    def common_upper_covers(
        self,
        members: Iterable[PosetElement],
    ) -> Iterator[PosetElement]:
        return self._realization().common_upper_covers(members)

    def open_interval(
        self,
        lower: PosetElement,
        upper: PosetElement,
    ) -> Iterator[PosetElement]:
        return self._realization().open_interval(lower, upper)

    def closed_interval(
        self,
        lower: PosetElement,
        upper: PosetElement,
    ) -> Iterator[PosetElement]:
        return self._realization().closed_interval(lower, upper)

    def principal_order_ideal(
        self,
        member: PosetElement,
    ) -> Iterator[PosetElement]:
        return self._realization().principal_order_ideal(member)

    def principal_order_filter(
        self,
        member: PosetElement,
    ) -> Iterator[PosetElement]:
        return self._realization().principal_order_filter(member)

    def order_ideal(
        self,
        members: Iterable[PosetElement],
    ) -> Iterator[PosetElement]:
        return self._realization().order_ideal(members)

    def order_filter(
        self,
        members: Iterable[PosetElement],
    ) -> Iterator[PosetElement]:
        return self._realization().order_filter(members)

    def minimal_elements(self) -> Iterator[PosetElement]:
        return self._realization().minimal_elements()

    def maximal_elements(self) -> Iterator[PosetElement]:
        return self._realization().maximal_elements()

    def has_bottom(self) -> bool:
        return self._realization().has_bottom()

    def bottom(self) -> PosetElement:
        return self._realization().bottom()

    def has_top(self) -> bool:
        return self._realization().has_top()

    def top(self) -> PosetElement:
        return self._realization().top()

    def is_bounded(self) -> bool:
        return self._realization().is_bounded()

    def height(self) -> int:
        return self._realization().height()

    def width(self) -> int:
        return self._realization().width()

    def rank(self, member: PosetElement | None = None) -> int:
        return self._realization().rank(member)

    def level_sets(self) -> Iterator[Iterator[PosetElement]]:
        return self._realization().level_sets()

    def is_ranked(self) -> bool:
        return self._realization().is_ranked()

    def is_graded(self) -> bool:
        return self._realization().is_graded()

    def is_chain(self) -> bool:
        return self._realization().is_chain()

    def is_chain_of_poset(self, members: Iterable[PosetElement]) -> bool:
        return self._realization().is_chain_of_poset(members)

    def is_antichain_of_poset(self, members: Iterable[PosetElement]) -> bool:
        return self._realization().is_antichain_of_poset(members)

    def linear_extension(self) -> Iterator[PosetElement]:
        return self._realization().linear_extension()


class FinitePosetsCategory(FullSubcategory):
    """The full subcategory of finite partially ordered sets."""

    ObjectType: type[FinitePosetObject] = FinitePosetObject

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
        poset = PartiallyOrderedSets().ObjectType(
            category=PartiallyOrderedSets(),
            underlying_set=underlying_set,
            relation=relation,
        )
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
