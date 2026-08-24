"""Total orders as a law-bearing subcategory of partially ordered sets."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeIs, cast

from sage_categories.abstract_categories.category_constructions import FullSubcategory
from sage_categories.abstract_categories.functors import (
    InclusionFunctor,
    NaturalIsomorphism,
    StructuralFunctor,
    compose_functors,
)
from sage_categories.abstract_categories.hom_categories import HomCategory, Isomorphism, is_isomorphism
from sage_categories.category import Category
from sage_categories.theories.poset_core import (
    PartiallyOrderedSets,
    PartiallyOrderedSetsCategory,
    PosetElement,
    PosetMorphism,
    PosetObject,
    PosetHomCategory,
    is_poset_element,
    is_poset_hom_category,
)
from sage_categories.values import Arrow, Decision, MathematicalElement, MathematicalObject, registered_element

if TYPE_CHECKING:
    from sage_categories.theories.finite_posets import FinitePosetObject, FinitePosetsCategory


# Total orders add a law to the poset representation.  They do not wrap the
# poset object, element, or arrow in a second Python implementation.
TotallyOrderedSetElement = PosetElement
TotallyOrderedSetObject = PosetObject
TotallyOrderedSetMorphism = PosetMorphism
TotallyOrderedSetHomCategory = PosetHomCategory
TotalOrderInclusionFunctor = InclusionFunctor
FiniteTotallyOrderedSetElement = PosetElement
FiniteTotallyOrderedSetObject = PosetObject


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


def _reclassify(
    poset: PosetObject | FinitePosetObject,
    category: Category,
) -> PosetObject:
    """Reuse one poset representation in a law-bearing category."""
    object_type = category.ObjectType
    return object_type(
        category=cast(PartiallyOrderedSetsCategory, category),
        underlying_set=PartiallyOrderedSets().underlying_set(poset),
        relation=poset.relation(),
    )


class FiniteTotallyOrderedSetsCategory(FullSubcategory):
    """The full subcategory of finite total orders."""

    ObjectType = PosetObject
    ElementType = PosetElement

    def __init__(self, total_orders: TotallyOrderedSetsCategory) -> None:
        self._finite_poset_functor: InclusionFunctor | None = None
        self._structural_coherence: Isomorphism | None = None
        super().__init__(
            total_orders,
            self._is_finite_total_order,
            name="Finite totally ordered sets",
            object_type=PosetObject,
            element_type=PosetElement,
        )

    def __call__(
        self,
        poset: PosetObject | TotallyOrderedSetObject,
    ) -> TotallyOrderedSetObject:
        if self.contains_finite_total_order(poset):
            return poset
        assert poset in PartiallyOrderedSets()
        totality = is_total_order(poset)
        assert totality is True
        return _reclassify(poset, self)

    def _is_finite_total_order(self, value: MathematicalObject) -> bool:
        return value in PartiallyOrderedSets() and PartiallyOrderedSets().underlying_set(value).is_finite() is True and is_total_order(value) is True

    def finite_poset_functor(self) -> InclusionFunctor:
        if self._finite_poset_functor is None:
            self._finite_poset_functor = InclusionFunctor(self, PartiallyOrderedSets().Finite())
        return self._finite_poset_functor

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return self.inclusion(), self.finite_poset_functor()

    def structural_coherences(self) -> tuple[Isomorphism, ...]:
        if self._structural_coherence is None:
            first = compose_functors(TotallyOrderedSets().inclusion(), self.inclusion())
            second = compose_functors(
                self.finite_poset_functor().codomain().inclusion(),
                self.finite_poset_functor(),
            )

            def component(source: MathematicalObject) -> Arrow:
                image = first(source)
                assert image is second(source)
                return PartiallyOrderedSets().identity(image)

            self._structural_coherence = NaturalIsomorphism(second, first, component, component)
            assert is_isomorphism(self._structural_coherence)
        return (self._structural_coherence,)

    def contains_finite_total_order(self, candidate: MathematicalObject) -> TypeIs[PosetObject]:
        return candidate in self

    def __repr__(self) -> str:
        return "Finite totally ordered sets"


class TotallyOrderedSetsCategory(Category):
    """Sets equipped with a proved total order."""

    ObjectType = PosetObject
    ElementType = PosetElement

    def __init__(self) -> None:
        self._inclusion: InclusionFunctor | None = None
        self._finite_orders: FiniteTotallyOrderedSetsCategory | None = None
        super().__init__(object_type=PosetObject, element_type=PosetElement)

    def __call__(
        self,
        poset: PosetObject | FinitePosetObject | TotallyOrderedSetObject,
    ) -> TotallyOrderedSetObject:
        if self.contains_total_order(poset):
            return poset
        assert poset in PartiallyOrderedSets()
        if PartiallyOrderedSets().underlying_set(poset).is_finite() is True:
            totality = is_total_order(poset)
            assert totality is True
            return self.Finite()(poset)
        assert False, f"Nonfinite poset {poset} requires a named total-order construction"

    def _ordinal_total_order(self, poset: PosetObject) -> TotallyOrderedSetObject:
        """Use the ordinal well-order theorem to admit an infinite order."""
        assert poset in PartiallyOrderedSets()
        return _reclassify(poset, self)

    def _hom_category_type(self) -> type[HomCategory]:
        return PosetHomCategory

    def Hom(self, domain: MathematicalObject, codomain: MathematicalObject) -> PosetHomCategory:
        category = Category.Hom(self, domain, codomain)
        assert is_poset_hom_category(category)
        return category

    def inclusion(self) -> InclusionFunctor:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(self, PartiallyOrderedSets())
        return self._inclusion

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return (self.inclusion(),)

    def contains_total_order(self, candidate: MathematicalObject) -> TypeIs[PosetObject]:
        return candidate in self

    def underlying_poset(self, source: MathematicalObject) -> PosetObject:
        assert source in self
        image = self.inclusion()(source)
        assert image in PartiallyOrderedSets()
        return image

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


def is_total_order_hom_category(category: HomCategory) -> TypeIs[PosetHomCategory]:
    return is_poset_hom_category(category) and category.base_category() in (TotallyOrderedSets(), FiniteTotallyOrderedSets())


def is_total_order_element(candidate: MathematicalObject) -> TypeIs[PosetElement]:
    element = registered_element(candidate)
    return element is candidate and element.ambient_object() in TotallyOrderedSets()


def is_total_order_element_type(candidate: type[MathematicalElement]) -> TypeIs[type[PosetElement]]:
    source = vars(candidate).get("_compiled_from")
    return candidate is PosetElement or source is PosetElement
