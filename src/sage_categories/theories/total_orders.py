"""Total orders as a law-bearing subcategory of partially ordered sets."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.abstract_categories.category_constructions import (
    FullSubcategory,
)
from sage_categories.abstract_categories.functors import (
    RestrictedStructuralFunctor,
    StructuralFunctor,
)
from sage_categories.category import Category
from sage_categories.theories.poset_core import (
    PartiallyOrderedSets,
    PartiallyOrderedSetsCategory,
    PosetElement,
    is_poset_element,
)
from sage_categories.theories.sets import (
    NaturalNumbers,
    SetElement,
    SetMorphism,
    SetObject,
    Sets,
)
from sage_categories.values import (
    Decision,
    MathematicalObject,
    TransportedArrow,
    TransportedElement,
    TransportedObject,
    registered_element,
)

if TYPE_CHECKING:
    from sage_categories.theories.finite_posets import FinitePosetsCategory


class FiniteTotalToFinitePosetFunctor(RestrictedStructuralFunctor):
    """Restrict a finite total-order refinement to its finite poset image."""

    def __init__(self, finite_total_orders: FiniteTotallyOrderedSetsCategory) -> None:
        super().__init__(
            finite_total_orders,
            FinitePosets(),
            TotallyOrderedSets().inclusion(),
        )


class FiniteTotalOrderObject(TransportedObject):
    """One finite total order."""


class FiniteTotalOrderElement(TransportedElement):
    """An element of one finite total order."""


class FiniteTotalOrderMorphism(TransportedArrow):
    """An order-preserving map between finite total orders."""


class FiniteTotallyOrderedSetsCategory(FullSubcategory):
    """The full subcategory of finite total orders."""

    ObjectType: type[FiniteTotalOrderObject] = FiniteTotalOrderObject
    ElementType: type[FiniteTotalOrderElement] = FiniteTotalOrderElement
    ArrowType: type[FiniteTotalOrderMorphism] = FiniteTotalOrderMorphism

    def __init__(self, total_orders: TotallyOrderedSetsCategory) -> None:
        self._finite_poset_functor: FiniteTotalToFinitePosetFunctor | None = None
        super().__init__(
            total_orders,
            self._is_finite_total_order,
            name="Finite totally ordered sets",
        )

    def _is_finite_total_order(self, value: MathematicalObject) -> Decision:
        total = TotallyOrderedSets().__contains__(value)
        if total is not True:
            return total
        return PartiallyOrderedSets().underlying_set(value).is_finite()

    def from_enumeration(
        self,
        enumeration: SetMorphism,
    ) -> FiniteTotalOrderObject:
        """Construct the finite total order established by an enumeration."""
        from sage_categories.theories.ordinals import Ordinals

        underlying_set = enumeration.domain()
        assert Sets().contains_set(underlying_set)
        assert underlying_set.is_finite() is True
        assert enumeration in Sets().Mono(underlying_set, NaturalNumbers())

        def ordered(left: SetElement, right: SetElement) -> Decision:
            assert left.ambient_object() is underlying_set
            assert right.ambient_object() is underlying_set
            left_position = enumeration(left).value()
            right_position = enumeration(right).value()
            assert Ordinals().contains_ordinal(left_position)
            assert Ordinals().contains_ordinal(right_position)
            return Ordinals()._is_lequal(left_position, right_position)

        relation = Sets().relation(
            underlying_set,
            Sets().binary_predicate(underlying_set, ordered),
        )
        poset = PartiallyOrderedSets()._construct(underlying_set, relation)
        result = self._refine_object(poset)
        assert self.contains_finite_total_order(result)
        return result

    def finite_poset_functor(self) -> FiniteTotalToFinitePosetFunctor:
        if self._finite_poset_functor is None:
            self._finite_poset_functor = FiniteTotalToFinitePosetFunctor(self)
        return self._finite_poset_functor

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return self.inclusion(), self.finite_poset_functor()

    def contains_finite_total_order(self, candidate: MathematicalObject) -> bool:
        return candidate in self

    def __repr__(self) -> str:
        return "Finite totally ordered sets"


class TotallyOrderedSetsCategory(FullSubcategory):
    """Sets equipped with a proved total order."""

    class ObjectType(TransportedObject):
        """One total order."""

    class ElementType(TransportedElement):
        """An element of one total order."""

    class ArrowType(TransportedArrow):
        """An order-preserving map between total orders."""

    def __init__(self) -> None:
        self._finite_orders: FiniteTotallyOrderedSetsCategory | None = None
        super().__init__(
            PartiallyOrderedSets(),
            self.__contains__,
            name="Totally ordered sets",
        )

    def __contains__(self, candidate: Any) -> Decision:
        value = registered_value(candidate)
        if value is None or not PartiallyOrderedSets().contains_poset(value):
            return False
        category = value.category()
        if category is self or category.is_subcategory(self):
            return True
        underlying_set = PartiallyOrderedSets().underlying_set(value)
        if underlying_set.is_finite() is not True:
            from sage_categories.values import UNKNOWN

            return UNKNOWN
        members = tuple(value)
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

    def contains_total_order(self, candidate: MathematicalObject) -> Decision:
        return self.__contains__(candidate)

    def natural_numbers_order(self) -> TotallyOrderedSetsCategory.ObjectType:
        """Construct the usual total order on the positive natural numbers."""
        poset = PartiallyOrderedSets().natural_numbers_order()
        return self._refine_object(poset)

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
