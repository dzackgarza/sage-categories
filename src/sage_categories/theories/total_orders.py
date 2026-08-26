"""Total orders as a law-bearing subcategory of partially ordered sets."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeIs

from sage_categories.abstract_categories.category_constructions import (
    FullSubcategory,
)
from sage_categories.abstract_categories.functors import (
    Functor,
    RestrictedConcreteFunctor,
    ConcreteFunctor,
)
from sage_categories.category import Category
from sage_categories.theories.poset_core import (
    PartiallyOrderedSets,
    PartiallyOrderedSetsCategory,
    PosetElement,
    PosetObject,
    is_poset_element,
)
from sage_categories.theories.sets import (
    SetMorphism,
    SetObject,
)
from sage_categories.types import (
    Arrow,
    Decision,
    MathematicalElement,
    MathematicalObject,
    registered_element,
)

if TYPE_CHECKING:
    from sage_categories.theories.finite_posets import FinitePosetsCategory


class FiniteTotalToFinitePosetFunctor(RestrictedConcreteFunctor):
    """Restrict a finite total-order refinement to its finite poset image."""

    def __init__(self, finite_total_orders: FiniteTotallyOrderedSetsCategory) -> None:
        super().__init__(
            finite_total_orders,
            FinitePosets(),
            TotallyOrderedSets().inclusion(),
        )


class TotalOrderObject(MathematicalObject):
    """One total order."""

    def is_total_order(self) -> Decision:
        return True


class TotalOrderElement(MathematicalElement):
    """An element of one total order."""


class TotalOrderMorphism(Arrow):
    """An order-preserving map between total orders."""


class FiniteTotalOrderObject(MathematicalObject):
    """One finite total order."""

    def is_finite(self) -> Decision:
        return True


class FiniteTotalOrderElement(MathematicalElement):
    """An element of one finite total order."""


class FiniteTotalOrderMorphism(Arrow):
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
            SetObject.is_finite,
            name="Finite totally ordered sets",
        )

    def __call__(
        self,
        enumeration: SetMorphism,
    ) -> FiniteTotalOrderObject:
        """Construct the finite total order established by an enumeration."""
        poset = PartiallyOrderedSets().order_from_enumeration(enumeration)
        result = super().__call__(poset)
        assert self.contains_finite_total_order(result)
        return result

    def finite_poset_functor(self) -> FiniteTotalToFinitePosetFunctor:
        if self._finite_poset_functor is None:
            self._finite_poset_functor = FiniteTotalToFinitePosetFunctor(self)
        return self._finite_poset_functor

    def structure_functors(self) -> tuple[Functor, ...]:
        return self.inclusion(), self.finite_poset_functor()

    def contains_finite_total_order(self, candidate: MathematicalObject) -> bool:
        return candidate in self

    def __repr__(self) -> str:
        return "Finite totally ordered sets"


class TotallyOrderedSetsCategory(FullSubcategory):
    """Sets equipped with a proved total order."""

    ObjectType = TotalOrderObject
    ElementType = TotalOrderElement
    ArrowType = TotalOrderMorphism

    def __init__(self) -> None:
        self._finite_orders: FiniteTotallyOrderedSetsCategory | None = None
        super().__init__(
            PartiallyOrderedSets(),
            PosetObject.is_total_order,
            name="Totally ordered sets",
        )

    def contains_total_order(self, candidate: MathematicalObject) -> bool:
        return candidate in self

    def natural_numbers_order(self) -> TotallyOrderedSetsCategory.ObjectType:
        """Construct the usual total order on the positive natural numbers."""
        poset = PartiallyOrderedSets().natural_numbers_order()
        return self(poset)

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
        _TOTALLY_ORDERED_SETS.Finite()
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
