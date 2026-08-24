"""Total orders as a law-bearing subcategory of partially ordered sets."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeIs

from sage_categories.abstract_categories.category_constructions import (
    FullSubcategory,
    FullSubcategoryArrow,
    FullSubcategoryElement,
    FullSubcategoryObject,
)
from sage_categories.abstract_categories.functors import (
    InclusionFunctor,
    NaturalIsomorphism,
    RestrictedStructuralFunctor,
    StructuralFunctor,
    compose_functors,
)
from sage_categories.abstract_categories.hom_categories import Isomorphism, is_isomorphism
from sage_categories.category import Category
from sage_categories.theories.poset_core import (
    PartiallyOrderedSets,
    PartiallyOrderedSetsCategory,
    PosetElement,
    PosetObject,
    is_poset_element,
)
from sage_categories.values import Arrow, Decision, MathematicalElement, MathematicalObject, registered_element

if TYPE_CHECKING:
    from sage_categories.theories.finite_posets import FinitePosetObject, FinitePosetsCategory


def is_total_order(poset: PosetObject | FinitePosetObject) -> Decision:
    """Return whether every pair of elements in ``poset`` is comparable."""
    underlying_set = PartiallyOrderedSets().underlying_set(poset)
    if underlying_set.is_finite() is not True:
        from sage_categories.values import UNKNOWN

        return UNKNOWN
    members = tuple(poset)
    answer: Decision = True
    for position, left in enumerate(members):
        assert is_poset_element(left)
        for right in members[position + 1 :]:
            assert is_poset_element(right)
            left_le = left <= right
            right_le = right <= left
            if left_le is True or right_le is True:
                continue
            if left_le is False and right_le is False:
                return False
            answer = UNKNOWN
    return answer


class FiniteTotalToFinitePosetFunctor(RestrictedStructuralFunctor):
    """Restrict a finite total-order refinement to its finite poset image."""

    def __init__(self, finite_total_orders: FiniteTotallyOrderedSetsCategory) -> None:
        super().__init__(
            finite_total_orders,
            FinitePosets(),
            TotallyOrderedSets().inclusion(),
        )


class FiniteTotalOrderObject(FullSubcategoryObject):
    """One finite total order."""


class FiniteTotalOrderElement(FullSubcategoryElement):
    """An element of one finite total order."""


class FiniteTotalOrderMorphism(FullSubcategoryArrow):
    """An order-preserving map between finite total orders."""


class FiniteTotallyOrderedSetsCategory(FullSubcategory):
    """The full subcategory of finite total orders."""

    ObjectType: type[FiniteTotalOrderObject] = FiniteTotalOrderObject
    ElementType: type[FiniteTotalOrderElement] = FiniteTotalOrderElement
    ArrowType: type[FiniteTotalOrderMorphism] = FiniteTotalOrderMorphism

    def __init__(self, total_orders: TotallyOrderedSetsCategory) -> None:
        self._finite_poset_functor: InclusionFunctor | None = None
        self._structural_coherence: Isomorphism | None = None
        super().__init__(
            total_orders,
            self._is_finite_total_order,
            name="Finite totally ordered sets",
        )

    def _is_finite_total_order(self, value: MathematicalObject) -> bool:
        return value in TotallyOrderedSets() and PartiallyOrderedSets().underlying_set(value).is_finite() is True

    def finite_poset_functor(self) -> InclusionFunctor:
        if self._finite_poset_functor is None:
            self._finite_poset_functor = FiniteTotalToFinitePosetFunctor(self)
        return self._finite_poset_functor

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return self.inclusion(), self.finite_poset_functor()

    def structural_coherences(self) -> tuple[Isomorphism, ...]:
        if self._structural_coherence is None:
            first = compose_functors(TotallyOrderedSets().inclusion(), self.inclusion())
            second = compose_functors(
                FinitePosets().inclusion(),
                self.finite_poset_functor(),
            )

            def component(source: MathematicalObject) -> Arrow:
                image = first(source)
                assert image is second(source)
                return PartiallyOrderedSets().identity(image)

            coherence = NaturalIsomorphism(second, first, component, component)
            assert is_isomorphism(coherence)
            self._structural_coherence = coherence
        return (self._structural_coherence,)

    def contains_finite_total_order(self, candidate: MathematicalObject) -> bool:
        return candidate in self

    def __repr__(self) -> str:
        return "Finite totally ordered sets"


class TotallyOrderedSetsCategory(FullSubcategory):
    """Sets equipped with a proved total order."""

    class ObjectType(FullSubcategoryObject):
        """One total order."""

    class ElementType(FullSubcategoryElement):
        """An element of one total order."""

    class ArrowType(FullSubcategoryArrow):
        """An order-preserving map between total orders."""

    def __init__(self) -> None:
        self._finite_orders: FiniteTotallyOrderedSetsCategory | None = None
        super().__init__(
            PartiallyOrderedSets(),
            self._is_total_order,
            name="Totally ordered sets",
        )

    def _is_total_order(self, value: MathematicalObject) -> bool:
        if not PartiallyOrderedSets().contains_poset(value):
            return False
        return is_total_order(value) is True

    def contains_total_order(self, candidate: MathematicalObject) -> bool:
        return candidate in self

    def Finite(self) -> FiniteTotallyOrderedSetsCategory:
        if self._finite_orders is None:
            self._finite_orders = FiniteTotallyOrderedSetsCategory(self)
        return self._finite_orders

    def __repr__(self) -> str:
        return "Totally ordered sets"


_TOTALLY_ORDERED_SETS: TotallyOrderedSetsCategory | None = None


def TotallyOrderedSets() -> TotallyOrderedSetsCategory:
    global _TOTALLY_ORDERED_SETS
    if _TOTALLY_ORDERED_SETS is None:
        _TOTALLY_ORDERED_SETS = TotallyOrderedSetsCategory()
    return _TOTALLY_ORDERED_SETS


def FinitePosets() -> FinitePosetsCategory:
    return PartiallyOrderedSets().Finite()


def FiniteTotallyOrderedSets() -> FiniteTotallyOrderedSetsCategory:
    return TotallyOrderedSets().Finite()


def is_totally_ordered_sets_category(category: Category) -> TypeIs[TotallyOrderedSetsCategory]:
    return category is TotallyOrderedSets()


def is_total_order_element(candidate: MathematicalObject) -> bool:
    element = registered_element(candidate)
    return element is candidate and element.ambient_object() in TotallyOrderedSets()
