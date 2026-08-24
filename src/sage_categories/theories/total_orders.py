"""Totally ordered sets and their structural inclusion."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TypeIs

from sage_categories.abstract_categories.category_constructions import (
    FullSubcategory,
)
from sage_categories.abstract_categories.functors import (
    NaturalIsomorphism,
    StructuralFunctor,
    compose_functors,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    Isomorphism,
    is_isomorphism,
)
from sage_categories.category import Category
from sage_categories.theories.finite_posets import (
    FinitePosetObject,
    FinitePosetsCategory,
)
from sage_categories.theories.poset_core import (
    PartiallyOrderedSets,
    PartiallyOrderedSetsCategory,
    PosetElement,
    PosetMorphism,
    PosetObject,
    is_poset_element,
    is_poset_hom_category,
)
from sage_categories.theories.sets import (
    EnumerationInjection,
    SetElement,
)
from sage_categories.values import (
    UNKNOWN,
    Arrow,
    Decision,
    MathematicalElement,
    MathematicalObject,
    registered_element,
    registered_value,
)


class TotallyOrderedSetElement(MathematicalElement):
    """An element of one totally ordered set."""

    def __init__(
        self,
        *,
        ambient_object: TotallyOrderedSetObject,
        poset_element: PosetElement,
    ) -> None:
        assert ambient_object in TotallyOrderedSets()
        inclusion = TotallyOrderedSets().inclusion()
        assert poset_element.ambient_poset() is inclusion.on_object(ambient_object)
        self._poset_element = poset_element
        super().__init__(
            category=ambient_object.category(),
            ambient_object=ambient_object,
        )

    def _poset_implementation(self) -> PosetElement:
        return self._poset_element

    def ambient_total_order(self) -> TotallyOrderedSetObject:
        ambient = self.ambient_object()
        assert TotallyOrderedSets().contains_total_order(ambient)
        return ambient

    def __le__(self, other: TotallyOrderedSetElement) -> bool:
        inclusion = TotallyOrderedSets().inclusion()
        other_poset_element = inclusion.on_element(other.ambient_total_order(), other)
        assert is_poset_element(other_poset_element)
        comparison = self._poset_element <= other_poset_element
        assert comparison is not UNKNOWN
        return comparison

    def __lt__(self, other: TotallyOrderedSetElement) -> bool:
        inclusion = TotallyOrderedSets().inclusion()
        other_poset_element = inclusion.on_element(other.ambient_total_order(), other)
        assert is_poset_element(other_poset_element)
        comparison = self._poset_element < other_poset_element
        assert comparison is not UNKNOWN
        return comparison

    def __repr__(self) -> str:
        return repr(self._poset_element)


class TotallyOrderedSetObject(MathematicalObject):
    """A poset whose order relation is total."""

    def __init__(
        self,
        *,
        category: TotallyOrderedSetsCategory,
        poset: PosetObject,
    ) -> None:
        self._poset = poset
        self._elements: dict[int, TotallyOrderedSetElement] = {}
        super().__init__(category=category)

    def _poset_implementation(self) -> PosetObject:
        return self._poset

    def element(self, poset_element: PosetElement) -> TotallyOrderedSetElement:
        assert poset_element.ambient_object() is self._poset
        key = id(poset_element)
        cached = self._elements.get(key)
        if cached is None:
            element_type = self.category().ElementType
            assert is_total_order_element_type(element_type)
            cached = element_type(
                ambient_object=self,
                poset_element=poset_element,
            )
            self._elements[key] = cached
        return cached

    def __repr__(self) -> str:
        return f"Totally ordered {PartiallyOrderedSets().underlying_set(self._poset)}"


class TotallyOrderedSetMorphism(Arrow):
    """A monotone map between two totally ordered sets."""

    def __init__(
        self,
        *,
        hom_category: TotallyOrderedSetHomCategory,
        poset_morphism: PosetMorphism,
    ) -> None:
        self._poset_morphism = poset_morphism
        super().__init__(hom_category=hom_category)

    def _poset_implementation(self) -> PosetMorphism:
        return self._poset_morphism

    def __call__(
        self,
        member: TotallyOrderedSetElement,
    ) -> MathematicalElement:
        category = self.base_category()
        assert is_totally_ordered_sets_category(category)
        source = self.domain()
        target = self.codomain()
        assert category.contains_total_order(source)
        assert category.contains_total_order(target)
        assert member in source
        inclusion = category.inclusion()
        poset_member = inclusion.on_element(source, member)
        assert is_poset_element(poset_member)
        image = self._poset_morphism(poset_member)
        return target.element(image)


class TotallyOrderedSetHomCategory(HomCategory):
    """The monotone maps between two totally ordered sets."""

    ObjectType = TotallyOrderedSetMorphism
    ElementType = TotallyOrderedSetMorphism

    def __call__(
        self,
        action: Callable[[TotallyOrderedSetElement], TotallyOrderedSetElement]
        | Mapping[TotallyOrderedSetElement, TotallyOrderedSetElement]
        | TotallyOrderedSetMorphism,
        *,
        injective: Decision = UNKNOWN,
        surjective: Decision = UNKNOWN,
    ) -> TotallyOrderedSetMorphism:
        category = self.base_category()
        assert is_totally_ordered_sets_category(category)
        domain = self.domain()
        codomain = self.codomain()
        assert category.contains_total_order(domain)
        assert category.contains_total_order(codomain)
        source = category.underlying_poset(domain)
        target = category.underlying_poset(codomain)
        poset_hom = PartiallyOrderedSets().Hom(source, target)
        assert is_poset_hom_category(poset_hom)

        existing = registered_value(action)
        if existing is not None:
            assert self.contains_total_order_morphism(existing)
            return existing

        def poset_action(member: PosetElement) -> PosetElement:
            source_member = domain.element(member)
            if callable(action):
                image = action(source_member)
            else:
                image = action[source_member]
            assert is_total_order_element(image)
            assert image in codomain
            poset_image = category.inclusion().on_element(codomain, image)
            assert is_poset_element(poset_image)
            return poset_image

        underlying = poset_hom(
            poset_action,
            injective=injective,
            surjective=surjective,
        )
        return self.ObjectType(
            hom_category=self,
            poset_morphism=underlying,
        )

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> TotallyOrderedSetMorphism:
        assert value is None
        assert self.domain() is self.codomain()
        category = self.base_category()
        assert is_totally_ordered_sets_category(category)
        domain = self.domain()
        assert category.contains_total_order(domain)
        source = category.underlying_poset(domain)
        underlying = PartiallyOrderedSets().identity(source)
        underlying_hom = underlying.hom_category()
        assert is_poset_hom_category(underlying_hom)
        assert underlying_hom.contains_poset_morphism(underlying)
        return self.ObjectType(
            hom_category=self,
            poset_morphism=underlying,
        )

    def compose(
        self,
        second: Arrow,
        first: Arrow,
    ) -> TotallyOrderedSetMorphism:
        second_hom = second.hom_category()
        first_hom = first.hom_category()
        assert is_total_order_hom_category(second_hom)
        assert is_total_order_hom_category(first_hom)
        assert second_hom.contains_total_order_morphism(second)
        assert first_hom.contains_total_order_morphism(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        category = self.base_category()
        assert is_totally_ordered_sets_category(category)
        inclusion = category.inclusion()
        underlying = PartiallyOrderedSets().compose(
            inclusion.on_morphism(second),
            inclusion.on_morphism(first),
        )
        underlying_hom = underlying.hom_category()
        assert is_poset_hom_category(underlying_hom)
        assert underlying_hom.contains_poset_morphism(underlying)
        return self.ObjectType(
            hom_category=self,
            poset_morphism=underlying,
        )

    def contains_total_order_morphism(
        self,
        arrow: MathematicalObject,
    ) -> TypeIs[TotallyOrderedSetMorphism]:
        return arrow in self


class TotalOrderInclusionFunctor(StructuralFunctor):
    """Regard a total order as its underlying partial order."""

    def __init__(
        self,
        total_orders: TotallyOrderedSetsCategory | FiniteTotallyOrderedSetsCategory,
        posets: PartiallyOrderedSetsCategory | FinitePosetsCategory,
    ) -> None:
        super().__init__(total_orders, posets)

    def _object_image(self, source: MathematicalObject) -> PosetObject:
        assert TotallyOrderedSets().contains_total_order(source)
        image = source._poset_implementation()
        assert image in self.codomain()
        return image

    def _morphism_image(self, morphism: Arrow) -> PosetMorphism:
        hom_category = morphism.hom_category()
        assert is_total_order_hom_category(hom_category)
        assert hom_category.contains_total_order_morphism(morphism)
        return morphism._poset_implementation()

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> PosetElement:
        assert TotallyOrderedSets().contains_total_order(source)
        assert is_total_order_element(element)
        return element._poset_implementation()

    def _element_preimage(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> TotallyOrderedSetElement:
        assert TotallyOrderedSets().contains_total_order(source)
        assert is_poset_element(element)
        element_type = source.category().ElementType
        assert is_total_order_element_type(element_type)
        preimage = element_type(
            ambient_object=source,
            poset_element=element,
        )
        assert is_total_order_element(preimage)
        return preimage

    def is_faithful(self) -> bool:
        return True

    def is_inclusion(self) -> bool:
        return True


class FiniteTotallyOrderedSetElement(MathematicalElement):
    """An element of one finite totally ordered set."""

    def __init__(
        self,
        *,
        ambient_object: FiniteTotallyOrderedSetObject,
        poset_element: PosetElement,
    ) -> None:
        self._poset_element = poset_element
        super().__init__(
            category=ambient_object.category(),
            ambient_object=ambient_object,
        )

    def _poset_implementation(self) -> PosetElement:
        return self._poset_element


class FiniteTotallyOrderedSetObject(MathematicalObject):
    """A finite totally ordered set."""

    def __init__(
        self,
        *,
        category: FiniteTotallyOrderedSetsCategory,
        poset: FinitePosetObject,
    ) -> None:
        assert FinitePosets().contains_finite_poset(poset)
        self._poset = poset
        self._elements: dict[int, FiniteTotallyOrderedSetElement] = {}
        super().__init__(category=category)

    def _poset_implementation(self) -> FinitePosetObject:
        return self._poset

    def element(self, poset_element: PosetElement) -> FiniteTotallyOrderedSetElement:
        assert poset_element.ambient_object() is self._poset
        key = id(poset_element)
        cached = self._elements.get(key)
        if cached is None:
            element_type = self.category().ElementType
            assert is_finite_total_order_element_type(element_type)
            cached = element_type(
                ambient_object=self,
                poset_element=poset_element,
            )
            self._elements[key] = cached
        return cached

    def __getitem__(self, position: int) -> FiniteTotallyOrderedSetElement:
        assert position >= 0
        members = tuple(self._poset.linear_extension())
        return self.element(members[position])

    def position(self, member: FiniteTotallyOrderedSetElement) -> int:
        assert member in self
        return tuple(self._poset.linear_extension()).index(
            member._poset_implementation()
        )

    def rank(self, member: FiniteTotallyOrderedSetElement) -> int:
        return self.position(member)

    def unrank(self, position: int) -> FiniteTotallyOrderedSetElement:
        return self[position]

    def enumeration_injection(self) -> Arrow:
        underlying_set = PartiallyOrderedSets().underlying_set(self._poset)

        def position_of_set_element(member: SetElement) -> int:
            return tuple(self._poset.linear_extension()).index(
                self._poset.element(member)
            )

        return EnumerationInjection(underlying_set, position_of_set_element)


class FiniteTotallyOrderedSetsCategory(FullSubcategory):
    """The full subcategory of finite totally ordered sets."""

    ObjectType: type[FiniteTotallyOrderedSetObject] = FiniteTotallyOrderedSetObject
    ElementType: type[FiniteTotallyOrderedSetElement] = FiniteTotallyOrderedSetElement

    def __init__(self, total_orders: TotallyOrderedSetsCategory) -> None:
        self._finite_poset_functor: TotalOrderInclusionFunctor | None = None
        self._structural_coherence: Isomorphism | None = None
        super().__init__(
            total_orders,
            self._is_finite,
            name="Finite totally ordered sets",
        )

    def __call__(
        self,
        poset: PosetObject,
    ) -> FiniteTotallyOrderedSetObject:
        assert FinitePosets().contains_finite_poset(poset)
        value = self.ObjectType(
            category=self,
            poset=poset,
        )
        assert self.contains_finite_total_order(value)
        return value

    def _is_finite(self, value: MathematicalObject) -> bool:
        assert TotallyOrderedSets().contains_total_order(value)
        return value._poset_implementation() in FinitePosets()

    def finite_poset_functor(self) -> TotalOrderInclusionFunctor:
        if self._finite_poset_functor is None:
            self._finite_poset_functor = TotalOrderInclusionFunctor(
                self,
                FinitePosets(),
            )
        return self._finite_poset_functor

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return self.inclusion(), self.finite_poset_functor()

    def structural_coherences(self) -> tuple[Isomorphism, ...]:
        if self._structural_coherence is None:
            first = compose_functors(
                TotallyOrderedSets().inclusion(),
                self.inclusion(),
            )
            second = compose_functors(
                FinitePosets().inclusion(),
                self.finite_poset_functor(),
            )

            def component(source: MathematicalObject) -> Arrow:
                image = first(source)
                assert image is second(source)
                return PartiallyOrderedSets().identity(image)

            coherence = NaturalIsomorphism(
                second,
                first,
                component,
                component,
            )
            assert is_isomorphism(coherence)
            self._structural_coherence = coherence
        return (self._structural_coherence,)

    def contains_finite_total_order(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[FiniteTotallyOrderedSetObject]:
        return candidate in self

    def __repr__(self) -> str:
        return "Finite totally ordered sets"


class TotallyOrderedSetsCategory(Category):
    """Sets equipped with a chosen total order."""

    ObjectType = TotallyOrderedSetObject
    ElementType = TotallyOrderedSetElement

    def __init__(self) -> None:
        self._inclusion: TotalOrderInclusionFunctor | None = None
        self._finite_orders: FiniteTotallyOrderedSetsCategory | None = None
        super().__init__()

    def __call__(
        self,
        poset: PosetObject,
    ) -> TotallyOrderedSetObject:
        if poset in FinitePosets():
            assert FinitePosets().contains_finite_poset(poset)
            return self.Finite()(poset)
        return self.ObjectType(
            category=self,
            poset=poset,
        )

    def _hom_category_type(self) -> type[HomCategory]:
        return TotallyOrderedSetHomCategory

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> TotallyOrderedSetHomCategory:
        assert codomain is not None
        category = Category.Hom(self, domain, codomain)
        assert is_total_order_hom_category(category)
        return category

    def inclusion(self) -> TotalOrderInclusionFunctor:
        if self._inclusion is None:
            self._inclusion = TotalOrderInclusionFunctor(
                self,
                PartiallyOrderedSets(),
            )
        return self._inclusion

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return (self.inclusion(),)

    def contains_total_order(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[TotallyOrderedSetObject]:
        return candidate in self

    def underlying_poset(self, source: MathematicalObject) -> PosetObject:
        assert source in self
        image = self.inclusion()(source)
        assert PartiallyOrderedSets().contains_poset(image)
        return image

    def Finite(self) -> FiniteTotallyOrderedSetsCategory:
        if self._finite_orders is None:
            self._finite_orders = FiniteTotallyOrderedSetsCategory(self)
        return self._finite_orders

    def __repr__(self) -> str:
        return "Totally ordered sets"


_TOTALLY_ORDERED_SETS: TotallyOrderedSetsCategory | None = None

_ORDERED_FINITE_SETS: dict[
    tuple[SetElement, ...],
    FiniteTotallyOrderedSetObject,
] = {}


def TotallyOrderedSets() -> TotallyOrderedSetsCategory:
    global _TOTALLY_ORDERED_SETS

    if _TOTALLY_ORDERED_SETS is None:
        _TOTALLY_ORDERED_SETS = TotallyOrderedSetsCategory()
    return _TOTALLY_ORDERED_SETS


def FinitePosets() -> FinitePosetsCategory:
    return PartiallyOrderedSets().Finite()


def FiniteTotallyOrderedSets() -> FiniteTotallyOrderedSetsCategory:
    return TotallyOrderedSets().Finite()


def is_totally_ordered_sets_category(
    category: Category,
) -> TypeIs[TotallyOrderedSetsCategory]:
    return category is TotallyOrderedSets()


def is_total_order_hom_category(
    category: HomCategory,
) -> TypeIs[TotallyOrderedSetHomCategory]:
    return (
        category.base_category() is TotallyOrderedSets()
        and category in TotallyOrderedSets().HomCategory()
    )


def is_total_order_element(
    candidate: MathematicalObject,
) -> TypeIs[TotallyOrderedSetElement]:
    element = registered_element(candidate)
    return element is candidate and element.ambient_object() in TotallyOrderedSets()


def is_total_order_element_type(
    candidate: type[MathematicalElement],
) -> TypeIs[type[TotallyOrderedSetElement]]:
    source = vars(candidate).get("_compiled_from")
    return candidate in (
        TotallyOrderedSetElement,
        FiniteTotallyOrderedSetElement,
    ) or source in (
        TotallyOrderedSetElement,
        FiniteTotallyOrderedSetElement,
    )


def is_finite_total_order_element_type(
    candidate: type[MathematicalElement],
) -> TypeIs[type[FiniteTotallyOrderedSetElement]]:
    return (
        candidate is FiniteTotallyOrderedSetElement
        or vars(candidate).get("_compiled_from") is FiniteTotallyOrderedSetElement
    )
