"""Partially ordered sets and their structural category."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import Any, TypeIs

from sage_categories.abstract_categories.functors import (
    Functor,
    StructuralFunctor,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
)
from sage_categories.category import Category
from sage_categories.theories.sets import (
    FiniteSet,
    FiniteSets,
    FiniteSetsCategory,
    SetElement,
    SetElements,
    SetMorphism,
    SetObject,
    Sets,
    SetsCategory,
    is_set_hom_category,
)
from sage_categories.values import (
    UNKNOWN,
    Arrow,
    Decision,
    MathematicalElement,
    MathematicalObject,
    registered_value,
)

type OrderRelation = Callable[[PosetElement, PosetElement], Decision]


class PosetElement(MathematicalElement):
    """An element of one partially ordered set."""

    def __init__(
        self,
        *,
        ambient_object: PosetObject | PosetProductObject,
        set_element: SetElement,
    ) -> None:
        assert ambient_object in PartiallyOrderedSets()
        underlying_set = PartiallyOrderedSets().underlying_set(ambient_object)
        assert set_element.ambient_set() is underlying_set
        assert set_element in underlying_set
        self._set_element = set_element
        super().__init__(
            category=PosetElements(),
            ambient_object=ambient_object,
        )

    def _set_implementation(self) -> SetElement:
        return self._set_element

    def ambient_poset(self) -> PosetObject | PosetProductObject:
        ambient = self.ambient_object()
        assert PartiallyOrderedSets().contains_poset(ambient)
        return ambient

    def __le__(self, other: PosetElement) -> Decision:
        return self.ambient_poset()._is_lequal(self, other)

    def __lt__(self, other: PosetElement) -> Decision:
        comparison = self <= other
        if comparison is UNKNOWN:
            return UNKNOWN
        return comparison and self != other

    def __repr__(self) -> str:
        return repr(self._set_element)


class PosetElementsCategory(Category):
    """The total category of elements of partially ordered sets."""

    ObjectType = PosetElement

    def __init__(self) -> None:
        super().__init__()

    def contains_poset_element(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[PosetElement]:
        return candidate in self

    def __repr__(self) -> str:
        return "Elements of partially ordered sets"


_POSET_ELEMENTS: PosetElementsCategory | None = None


def PosetElements() -> PosetElementsCategory:
    global _POSET_ELEMENTS

    if _POSET_ELEMENTS is None:
        _POSET_ELEMENTS = PosetElementsCategory()
    return _POSET_ELEMENTS


class PosetObject(MathematicalObject):
    """A set equipped with one chosen partial order."""

    def __init__(
        self,
        *,
        category: (
            PartiallyOrderedSetsCategory
            | FinitePosetsCategory
            | ProductsOfPosetsCategory
        ),
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> None:
        assert underlying_set in Sets()
        self._underlying_set = underlying_set
        self._relation = relation
        self._elements: dict[int, PosetElement] = {}
        self._thin_category: ThinCategory | None = None
        super().__init__(category=category)

    def _set_implementation(self) -> SetObject:
        return self._underlying_set

    def element(self, set_element: SetElement) -> PosetElement:
        assert set_element.ambient_set() is self._underlying_set
        assert set_element in self._underlying_set
        key = id(set_element)
        cached = self._elements.get(key)
        if cached is None:
            cached = PartiallyOrderedSets().ElementType(
                ambient_object=self,
                set_element=set_element,
            )
            self._elements[key] = cached
        return cached

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return (
            value is not None
            and PosetElements().contains_poset_element(value)
            and value.ambient_poset() is self
        )

    def __iter__(self) -> Iterator[PosetElement]:
        return iter(self.element(member) for member in self._underlying_set)

    def _is_lequal(self, left: PosetElement, right: PosetElement) -> Decision:
        assert left in self
        assert right in self
        return self._relation(left, right)

    def thin_category(self) -> ThinCategory:
        if self._thin_category is None:
            self._thin_category = ThinCategory(self)
        return self._thin_category

    def __repr__(self) -> str:
        return f"Partially ordered {self._underlying_set}"


class PosetMorphism(Arrow):
    """An order-preserving map with its underlying set function."""

    def __init__(
        self,
        *,
        hom_category: PosetHomCategory,
        underlying_function: SetMorphism,
    ) -> None:
        source = hom_category.domain()
        target = hom_category.codomain()
        category = hom_category.base_category()
        assert is_partially_ordered_sets_category(category)
        assert category.contains_poset(source)
        assert category.contains_poset(target)
        assert underlying_function in Sets().Hom(
            category.underlying_set(source),
            category.underlying_set(target),
        )
        self._underlying_function = underlying_function
        super().__init__(hom_category=hom_category)

    def _set_implementation(self) -> SetMorphism:
        return self._underlying_function

    def __call__(self, member: PosetElement) -> PosetElement:
        source = self.domain()
        target = self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        assert category.contains_poset(source)
        assert category.contains_poset(target)
        assert member in source
        forgetful_functor = category.forgetful_functor()
        set_member = forgetful_functor.on_element(source, member)
        assert SetElements().contains_set_element(set_member)
        image = self._underlying_function(set_member)
        return target.element(image)

    def is_order_preserving(self) -> bool:
        return True

    def is_order_reflecting(self) -> Decision:
        source = self.domain()
        target = self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        assert category.contains_poset(source)
        assert category.contains_poset(target)
        underlying_set = category.underlying_set(source)
        if underlying_set.is_finite() is not True:
            return UNKNOWN
        answer: Decision = True
        for left in source:
            for right in source:
                image_comparison = self(left) <= self(right)
                source_comparison = left <= right
                if image_comparison is True and source_comparison is False:
                    return False
                if image_comparison is UNKNOWN or source_comparison is UNKNOWN:
                    answer = UNKNOWN
        return answer

    def is_order_embedding(self) -> Decision:
        return self.is_order_reflecting()

    def is_order_isomorphism(self) -> Decision:
        bijective = self._underlying_function.is_bijective()
        reflecting = self.is_order_reflecting()
        if bijective is False or reflecting is False:
            return False
        if bijective is UNKNOWN or reflecting is UNKNOWN:
            return UNKNOWN
        return True

    def inverse(self) -> PosetMorphism:
        assert self.is_order_isomorphism() is True
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        inverse = self._underlying_function.inverse()
        hom_category = category.Hom(self.codomain(), self.domain())
        assert is_poset_hom_category(hom_category)
        return hom_category.ObjectType(
            hom_category=hom_category,
            underlying_function=inverse,
        )


class PosetHomCategory(HomCategory):
    """The order-preserving maps between two posets."""

    ObjectType = PosetMorphism
    ElementType = PosetMorphism

    def __call__(
        self,
        action: Callable[[PosetElement], PosetElement]
        | Mapping[PosetElement, PosetElement]
        | PosetMorphism,
        *,
        injective: Decision = UNKNOWN,
        surjective: Decision = UNKNOWN,
    ) -> PosetMorphism:
        existing = registered_value(action)
        if existing is not None:
            assert self.contains_poset_morphism(existing)
            return existing
        source = self.domain()
        target = self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        assert category.contains_poset(source)
        assert category.contains_poset(target)
        set_hom = Sets().Hom(
            category.underlying_set(source),
            category.underlying_set(target),
        )
        assert is_set_hom_category(set_hom)

        def underlying_action(member: SetElement) -> SetElement:
            source_member = source.element(member)
            if callable(action):
                image = action(source_member)
            else:
                image = action[source_member]
            assert PosetElements().contains_poset_element(image)
            assert image in target
            set_image = category.forgetful_functor().on_element(target, image)
            assert SetElements().contains_set_element(set_image)
            return set_image

        underlying = set_hom(
            underlying_action,
            injective=injective,
            surjective=surjective,
        )
        return self.ObjectType(
            hom_category=self,
            underlying_function=underlying,
        )

    def identity(self, value: MathematicalObject | None = None) -> PosetMorphism:
        assert value is None
        assert self.domain() is self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        source = self.domain()
        assert category.contains_poset(source)
        underlying = Sets().identity(category.underlying_set(source))
        assert Sets().contains_set_morphism(underlying)
        return self.ObjectType(
            hom_category=self,
            underlying_function=underlying,
        )

    def compose(self, second: Arrow, first: Arrow) -> PosetMorphism:
        second_hom = second.hom_category()
        first_hom = first.hom_category()
        assert is_poset_hom_category(second_hom)
        assert is_poset_hom_category(first_hom)
        assert second_hom.contains_poset_morphism(second)
        assert first_hom.contains_poset_morphism(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        forgetful_functor = category.forgetful_functor()
        underlying = Sets().compose(
            forgetful_functor.on_morphism(second),
            forgetful_functor.on_morphism(first),
        )
        assert Sets().contains_set_morphism(underlying)
        return self.ObjectType(
            hom_category=self,
            underlying_function=underlying,
        )

    def contains_poset_morphism(
        self,
        arrow: MathematicalObject,
    ) -> TypeIs[PosetMorphism]:
        return arrow in self


class ForgetPosetFunctor(StructuralFunctor):
    """Forget the chosen order and retain the underlying set and function."""

    def __init__(
        self,
        posets: PartiallyOrderedSetsCategory | FinitePosetsCategory,
        sets: SetsCategory | FiniteSetsCategory,
    ) -> None:
        super().__init__(posets, sets)

    def _object_image(self, source: MathematicalObject) -> SetObject:
        assert PartiallyOrderedSets().contains_poset(source)
        image = source._set_implementation()
        assert image in self.codomain()
        return image

    def _morphism_image(self, morphism: Arrow) -> SetMorphism:
        hom_category = morphism.hom_category()
        assert is_poset_hom_category(hom_category)
        assert hom_category.contains_poset_morphism(morphism)
        return morphism._set_implementation()

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> SetElement:
        assert PartiallyOrderedSets().contains_poset(source)
        assert PosetElements().contains_poset_element(element)
        assert element in source
        return element._set_implementation()

    def is_faithful(self) -> bool:
        return True


class PartiallyOrderedSetsCategory(Category):
    """Sets equipped with a chosen partial order."""

    ObjectType = PosetObject
    ElementType = PosetElement

    def __init__(self) -> None:
        self._forgetful_functor: ForgetPosetFunctor | None = None
        self._finite_posets: FinitePosetsCategory | None = None
        super().__init__()

    def __call__(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> PosetObject:
        if underlying_set in FiniteSets():
            return self.Finite()(underlying_set, relation)
        return self.ObjectType(
            category=self,
            underlying_set=underlying_set,
            relation=relation,
        )

    def _hom_category_type(self) -> type[HomCategory]:
        return PosetHomCategory

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> PosetHomCategory:
        assert codomain is not None
        category = Category.Hom(self, domain, codomain)
        assert is_poset_hom_category(category)
        return category

    def forgetful_functor(self) -> ForgetPosetFunctor:
        if self._forgetful_functor is None:
            self._forgetful_functor = ForgetPosetFunctor(self, Sets())
        return self._forgetful_functor

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return (self.forgetful_functor(),)

    def contains_poset(self, candidate: MathematicalObject) -> TypeIs[PosetObject]:
        return candidate in self

    def underlying_set(self, source: MathematicalObject) -> SetObject:
        assert source in self
        image = self.forgetful_functor()(source)
        assert Sets().contains_set(image)
        return image

    def Finite(self) -> FinitePosetsCategory:
        if self._finite_posets is None:
            self._finite_posets = FinitePosetsCategory(self)
        return self._finite_posets

    def _products_of_category(self, functor: Functor) -> Category:
        return ProductsOfPosetsCategory(functor)

    def __repr__(self) -> str:
        return "Partially ordered sets"


type PosetEnumeration = Callable[[int], PosetElement]

type PosetPosition = Callable[[PosetElement], int]


_PARTIALLY_ORDERED_SETS: PartiallyOrderedSetsCategory | None = None


def PartiallyOrderedSets() -> PartiallyOrderedSetsCategory:
    global _PARTIALLY_ORDERED_SETS

    if _PARTIALLY_ORDERED_SETS is None:
        _PARTIALLY_ORDERED_SETS = PartiallyOrderedSetsCategory()
    return _PARTIALLY_ORDERED_SETS


def Poset(
    members_and_relation: tuple[
        Iterable[SetElement],
        Callable[[SetElement, SetElement], Decision],
    ],
) -> FinitePosetObject:
    """Construct the finite poset defined by ``(members, leq)``."""
    members, relation = members_and_relation
    values = tuple(dict.fromkeys(members))
    underlying_set = FiniteSet(values)

    def transported_relation(left: PosetElement, right: PosetElement) -> Decision:
        forgetful_functor = PartiallyOrderedSets().forgetful_functor()
        left_element = forgetful_functor.on_element(left.ambient_poset(), left)
        right_element = forgetful_functor.on_element(right.ambient_poset(), right)
        assert SetElements().contains_set_element(left_element)
        assert SetElements().contains_set_element(right_element)
        left_value = left_element.value()
        right_value = right_element.value()
        assert SetElements().contains_set_element(left_value)
        assert SetElements().contains_set_element(right_value)
        return relation(left_value, right_value)

    poset = PartiallyOrderedSets()(underlying_set, transported_relation)
    assert FinitePosets().contains_finite_poset(poset)
    return poset


def is_partially_ordered_sets_category(
    category: Category,
) -> TypeIs[PartiallyOrderedSetsCategory]:
    return category is PartiallyOrderedSets()


def is_poset_hom_category(
    category: HomCategory,
) -> TypeIs[PosetHomCategory]:
    return (
        category.base_category() is PartiallyOrderedSets()
        and category in PartiallyOrderedSets().HomCategory()
    )


from sage_categories.theories.finite_posets import (
    FinitePosetObject,
    FinitePosetsCategory,
)
from sage_categories.theories.poset_products import (
    ForgetPosetProductFunctor,
    PosetProductObject,
    ProductsOfPosetsCategory,
)
from sage_categories.theories.thin_categories import (
    ThinCategory,
    ThinCategoryArrow,
    ThinCategoryArrowElement,
    ThinCategoryArrowSet,
    ThinCategoryHom,
    ThinCategoryObjectElement,
    ThinCategoryObjectSet,
    is_thin_category,
    is_thin_category_hom,
)
from sage_categories.theories.total_orders import (
    FinitePosets,
    FiniteTotallyOrderedSetObject,
    FiniteTotallyOrderedSets,
    FiniteTotallyOrderedSetsCategory,
    SimplexOrderIndexing,
    SimplexOrders,
    TotallyOrderedSetElement,
    TotallyOrderedSetElements,
    TotallyOrderedSetElementsCategory,
    TotallyOrderedSetHomCategory,
    TotallyOrderedSetMorphism,
    TotallyOrderedSetObject,
    TotallyOrderedSets,
    TotallyOrderedSetsCategory,
    TotalOrderInclusionFunctor,
    finite_ordered_set,
    is_total_order_hom_category,
    is_totally_ordered_sets_category,
    ordered_set_owned_by,
)

__all__ = (
    "FinitePosetObject",
    "FinitePosets",
    "FinitePosetsCategory",
    "FiniteTotallyOrderedSetObject",
    "FiniteTotallyOrderedSets",
    "FiniteTotallyOrderedSetsCategory",
    "ForgetPosetFunctor",
    "ForgetPosetProductFunctor",
    "OrderRelation",
    "PartiallyOrderedSets",
    "PartiallyOrderedSetsCategory",
    "Poset",
    "PosetElement",
    "PosetElements",
    "PosetElementsCategory",
    "PosetEnumeration",
    "PosetHomCategory",
    "PosetMorphism",
    "PosetObject",
    "PosetPosition",
    "PosetProductObject",
    "ProductsOfPosetsCategory",
    "SimplexOrderIndexing",
    "SimplexOrders",
    "ThinCategory",
    "ThinCategoryArrow",
    "ThinCategoryArrowElement",
    "ThinCategoryArrowSet",
    "ThinCategoryHom",
    "ThinCategoryObjectElement",
    "ThinCategoryObjectSet",
    "TotalOrderInclusionFunctor",
    "TotallyOrderedSetElement",
    "TotallyOrderedSetElements",
    "TotallyOrderedSetElementsCategory",
    "TotallyOrderedSetHomCategory",
    "TotallyOrderedSetMorphism",
    "TotallyOrderedSetObject",
    "TotallyOrderedSets",
    "TotallyOrderedSetsCategory",
    "finite_ordered_set",
    "is_partially_ordered_sets_category",
    "is_poset_hom_category",
    "is_thin_category",
    "is_thin_category_hom",
    "is_total_order_hom_category",
    "is_totally_ordered_sets_category",
    "ordered_set_owned_by",
)
