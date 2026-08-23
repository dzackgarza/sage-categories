"""Partially and totally ordered sets over the owned ``Sets`` category.

The mathematical surface follows ``specs/ordered-sets.md`` and the mature
Sage finite-poset interface.  Ordered objects and arrows retain their set
implementations through explicit structural functors.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.abstract_categories.category_constructions import (
    PullbackCategory,
    PullbackObject,
)
from sage_categories.abstract_categories.functors import (
    Functor,
    StructuralFunctor,
    compose_functors,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
)
from sage_categories.category import Category
from sage_categories.theories.sets import (
    EnumerationInjection,
    FiniteSet,
    FiniteSets,
    NaturalNumbers,
    SetElement,
    SetElements,
    SetMorphism,
    SetObject,
    Sets,
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

if TYPE_CHECKING:
    from sage_categories.backends.sage.finite_posets import (
        SageFinitePosetObject,
    )
    from sage_categories.theories.cardinals import Cardinal

type OrderRelation = Callable[[PosetElement, PosetElement], Decision]
type PosetMorphismDefinition = Callable[[PosetElement], PosetElement] | Mapping[PosetElement, PosetElement]


class PosetElement(MathematicalElement):
    """An element of one partially ordered set."""

    def __init__(
        self,
        *,
        ambient_object: PosetObject,
        set_element: SetElement,
    ) -> None:
        assert ambient_object in PartiallyOrderedSets()
        underlying_set = PartiallyOrderedSets().underlying_set(ambient_object)
        assert set_element.ambient_set() is underlying_set
        assert underlying_set._membership(set_element) is True
        self._set_element = set_element
        super().__init__(
            category=PosetElements(),
            ambient_object=ambient_object,
        )

    def _set_implementation(self) -> SetElement:
        return self._set_element

    def ambient_poset(self) -> PosetObject:
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
        super().__init__(object_type=PosetElement)

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
        category: PartiallyOrderedSetsCategory,
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
        assert self._underlying_set._membership(set_element) is True
        key = id(set_element)
        cached = self._elements.get(key)
        if cached is None:
            cached = PartiallyOrderedSets().ElementType(
                ambient_object=self,
                set_element=set_element,
            )
            self._elements[key] = cached
        return cached

    def _membership(self, member: PosetElement) -> Decision:
        assert PosetElements().contains_poset_element(member)
        return member.ambient_poset() is self

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and PosetElements().contains_poset_element(value) and self._membership(value) is True

    def __iter__(self) -> Iterator[PosetElement]:
        return iter(self.element(member) for member in self._underlying_set)

    def _is_lequal(self, left: PosetElement, right: PosetElement) -> Decision:
        assert self._membership(left) is True
        assert self._membership(right) is True
        return self._relation(left, right)

    def thin_category(self) -> ThinCategory:
        if self._thin_category is None:
            self._thin_category = ThinCategory(self)
        return self._thin_category

    def __repr__(self) -> str:
        return f"Partially ordered {self._underlying_set}"


class ThinCategoryObjectElement(SetElement):
    """A poset element regarded as an object name in its thin category."""

    def __init__(
        self,
        *,
        ambient_object: ThinCategoryObjectSet,
        value: PosetElement,
    ) -> None:
        self._value = value
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_object,
        )

    def value(self) -> PosetElement:
        return self._value


class ThinCategoryObjectSet(SetObject):
    """The set of objects in the thin category of one poset."""

    def __init__(self, category: ThinCategory) -> None:
        self._thin_category = category
        self._elements: dict[int, ThinCategoryObjectElement] = {}
        underlying_set = PartiallyOrderedSets().underlying_set(category.poset())
        super().__init__(
            category=Sets(),
            cardinality=underlying_set.cardinality(),
        )

    def element(self, value: PosetElement) -> ThinCategoryObjectElement:
        assert self._thin_category.contains_object(value)
        key = id(value)
        cached = self._elements.get(key)
        if cached is None:
            cached = ThinCategoryObjectElement(
                ambient_object=self,
                value=value,
            )
            self._elements[key] = cached
        return cached

    def _membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def __iter__(self) -> Iterator[SetElement]:
        return iter(self.element(value) for value in self._thin_category.poset())


class ThinCategoryArrow(Arrow):
    """The unique arrow represented by one valid poset comparison."""

    def __repr__(self) -> str:
        return f"{self.domain()} <= {self.codomain()}"


class ThinCategoryHom(HomCategory):
    """The empty or singleton Hom category of one poset comparison."""

    ObjectType = ThinCategoryArrow
    ElementType = ThinCategoryArrow

    def __init__(
        self,
        *,
        domain: MathematicalObject,
        codomain: MathematicalObject,
        hom_category: HomCategoryFamily,
    ) -> None:
        self._unique_morphism: ThinCategoryArrow | None = None
        super().__init__(
            domain=domain,
            codomain=codomain,
            hom_category=hom_category,
        )
        _THIN_HOM_CATEGORIES[id(self)] = self

    def comparison(self) -> Decision:
        category = self.base_category()
        assert is_thin_category(category)
        domain = self.domain()
        codomain = self.codomain()
        assert category.contains_object(domain)
        assert category.contains_object(codomain)
        return domain <= codomain

    def unique_morphism(self) -> ThinCategoryArrow:
        assert self.comparison() is True
        if self._unique_morphism is None:
            self._unique_morphism = self.ObjectType(hom_category=self)
        return self._unique_morphism

    def __call__(self) -> ThinCategoryArrow:
        return self.unique_morphism()

    def objects(self) -> SetObject:
        comparison = self.comparison()
        assert comparison is not UNKNOWN
        if comparison is False:
            return FiniteSet(())
        return FiniteSet((self.unique_morphism(),))

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> ThinCategoryArrow:
        assert value is None
        assert self.domain() is self.codomain()
        return self.unique_morphism()

    def compose(self, second: Arrow, first: Arrow) -> ThinCategoryArrow:
        assert first in self.base_category().ArrowCategory()
        assert second in self.base_category().ArrowCategory()
        assert first.codomain() is second.domain()
        return self.unique_morphism()


_THIN_HOM_CATEGORIES: dict[int, ThinCategoryHom] = {}


def is_thin_category_hom(
    category: MathematicalObject,
) -> TypeIs[ThinCategoryHom]:
    return _THIN_HOM_CATEGORIES.get(id(category)) is category


class ThinCategoryArrowElement(SetElement):
    """A thin-category arrow regarded as a member of its arrow set."""

    def __init__(
        self,
        *,
        ambient_object: ThinCategoryArrowSet,
        value: ThinCategoryArrow,
    ) -> None:
        self._value = value
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_object,
        )

    def value(self) -> ThinCategoryArrow:
        return self._value


class ThinCategoryArrowSet(SetObject):
    """The set of arrows in one thin category."""

    def __init__(self, category: ThinCategory) -> None:
        self._thin_category = category
        self._elements: dict[int, ThinCategoryArrowElement] = {}
        super().__init__(category=Sets())

    def element(self, value: ThinCategoryArrow) -> ThinCategoryArrowElement:
        assert value in self._thin_category.ArrowCategory()
        key = id(value)
        cached = self._elements.get(key)
        if cached is None:
            cached = ThinCategoryArrowElement(
                ambient_object=self,
                value=value,
            )
            self._elements[key] = cached
        return cached

    def _membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def __iter__(self) -> Iterator[SetElement]:
        poset = self._thin_category.poset()
        underlying_set = PartiallyOrderedSets().underlying_set(poset)
        assert underlying_set.is_finite() is True
        for source in poset:
            for target in poset:
                comparison = source <= target
                assert comparison is not UNKNOWN
                if comparison:
                    hom_category = self._thin_category.Hom(source, target)
                    yield self.element(hom_category())


class ThinCategory(Category):
    """The thin category associated to one partially ordered set."""

    ObjectType = PosetElement

    def __init__(self, poset: PosetObject) -> None:
        assert PartiallyOrderedSets().contains_poset(poset)
        self._poset = poset
        self._objects: ThinCategoryObjectSet | None = None
        self._arrows: ThinCategoryArrowSet | None = None
        super().__init__(object_type=PosetElement)
        _THIN_CATEGORIES[id(self)] = self

    def poset(self) -> PosetObject:
        return self._poset

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and self.contains_object(value)

    def contains_object(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[PosetElement]:
        return PosetElements().contains_poset_element(candidate) and candidate.ambient_poset() is self._poset

    def objects(self) -> ThinCategoryObjectSet:
        if self._objects is None:
            self._objects = ThinCategoryObjectSet(self)
        return self._objects

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> ThinCategoryHom:
        assert codomain is not None
        category = Category.Hom(self, domain, codomain)
        assert is_thin_category_hom(category)
        return category

    def arrows(self) -> ThinCategoryArrowSet:
        if self._arrows is None:
            self._arrows = ThinCategoryArrowSet(self)
        return self._arrows

    def _hom_category_type(self) -> type[HomCategory]:
        return ThinCategoryHom

    def __repr__(self) -> str:
        return f"Thin category of {self._poset}"


_THIN_CATEGORIES: dict[int, ThinCategory] = {}


def is_thin_category(category: Category) -> TypeIs[ThinCategory]:
    return _THIN_CATEGORIES.get(id(category)) is category


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
        assert source._membership(member) is True
        image = self._underlying_function(member._set_implementation())
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
        definition: PosetMorphismDefinition | PosetMorphism,
        *,
        injective: Decision = UNKNOWN,
        surjective: Decision = UNKNOWN,
    ) -> PosetMorphism:
        existing = registered_value(definition)
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
            if callable(definition):
                image = definition(source_member)
            else:
                image = definition[source_member]
            assert PosetElements().contains_poset_element(image)
            assert target._membership(image) is True
            return image._set_implementation()

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
        assert self.contains_poset_morphism(second)
        assert self.contains_poset_morphism(first)
        assert first.codomain() is second.domain()
        underlying = Sets().compose(
            second._set_implementation(),
            first._set_implementation(),
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

    def __init__(self, posets: PartiallyOrderedSetsCategory) -> None:
        self._posets = posets
        super().__init__(posets, Sets())

    def on_object(self, source: MathematicalObject) -> SetObject:
        assert self._posets.contains_poset(source)
        return source._set_implementation()

    def on_morphism(self, morphism: Arrow) -> SetMorphism:
        hom_category = morphism.hom_category()
        assert is_poset_hom_category(hom_category)
        assert hom_category.contains_poset_morphism(morphism)
        return morphism._set_implementation()

    def on_element(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> SetElement:
        assert self._posets.contains_poset(source)
        assert PosetElements().contains_poset_element(element)
        assert element.ambient_poset() is source
        return element._set_implementation()

    def is_faithful(self) -> bool:
        return True


class FinitePosetObject(PullbackObject):
    """A represented finite poset with finite order algorithms."""

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


class FinitePosetsCategory(PullbackCategory):
    """The pullback of posets and finite sets over sets."""

    def __init__(self, first: Functor, second: Functor) -> None:
        super().__init__(first, second, object_type=FinitePosetObject)

    def __repr__(self) -> str:
        return "Finite partially ordered sets"


class PartiallyOrderedSetsCategory(Category):
    """Sets equipped with a chosen partial order."""

    ObjectType = PosetObject
    ElementType = PosetElement

    def __init__(self) -> None:
        self._forgetful_functor: ForgetPosetFunctor | None = None
        self._finite_posets: FinitePosetsCategory | None = None
        super().__init__(
            object_type=PosetObject,
            element_type=PosetElement,
        )

    def __call__(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> PosetObject:
        return self.ObjectType(
            category=self,
            underlying_set=underlying_set,
            relation=relation,
        )

    def _hom_category_type(self) -> type[HomCategory]:
        return PosetHomCategory

    def forgetful_functor(self) -> ForgetPosetFunctor:
        if self._forgetful_functor is None:
            self._forgetful_functor = ForgetPosetFunctor(self)
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
            finite_to_countable = FiniteSets().super_functors()[0]
            countable_to_sets = finite_to_countable.codomain().super_functors()[0]
            finite_to_sets = compose_functors(
                countable_to_sets,
                finite_to_countable,
            )
            self._finite_posets = FinitePosetsCategory(
                self.forgetful_functor(),
                finite_to_sets,
            )
        return self._finite_posets

    def __repr__(self) -> str:
        return "Partially ordered sets"


type PosetEnumeration = Callable[[int], PosetElement]
type PosetPosition = Callable[[PosetElement], int]
type TotalOrderMorphismDefinition = Callable[[TotallyOrderedSetElement], TotallyOrderedSetElement] | Mapping[TotallyOrderedSetElement, TotallyOrderedSetElement]


class TotallyOrderedSetElement(MathematicalElement):
    """An element of one totally ordered set."""

    def __init__(
        self,
        *,
        ambient_object: TotallyOrderedSetObject,
        poset_element: PosetElement,
    ) -> None:
        assert ambient_object in TotallyOrderedSets()
        assert poset_element.ambient_poset() is ambient_object._poset_implementation()
        self._poset_element = poset_element
        super().__init__(
            category=TotallyOrderedSetElements(),
            ambient_object=ambient_object,
        )

    def _poset_implementation(self) -> PosetElement:
        return self._poset_element

    def ambient_total_order(self) -> TotallyOrderedSetObject:
        ambient = self.ambient_object()
        assert TotallyOrderedSets().contains_total_order(ambient)
        return ambient

    def position(self) -> int:
        return self.ambient_total_order().position(self)

    def rank(self) -> int:
        return self.position()

    def __le__(self, other: TotallyOrderedSetElement) -> bool:
        comparison = self._poset_element <= other._poset_implementation()
        assert comparison is not UNKNOWN
        return comparison

    def __lt__(self, other: TotallyOrderedSetElement) -> bool:
        comparison = self._poset_element < other._poset_implementation()
        assert comparison is not UNKNOWN
        return comparison

    def __repr__(self) -> str:
        return repr(self._poset_element)


class TotallyOrderedSetElementsCategory(Category):
    """The total category of elements of totally ordered sets."""

    ObjectType = TotallyOrderedSetElement

    def __init__(self) -> None:
        super().__init__(object_type=TotallyOrderedSetElement)

    def contains_total_order_element(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[TotallyOrderedSetElement]:
        return candidate in self

    def __repr__(self) -> str:
        return "Elements of totally ordered sets"


_TOTALLY_ORDERED_SET_ELEMENTS: TotallyOrderedSetElementsCategory | None = None


def TotallyOrderedSetElements() -> TotallyOrderedSetElementsCategory:
    global _TOTALLY_ORDERED_SET_ELEMENTS

    if _TOTALLY_ORDERED_SET_ELEMENTS is None:
        _TOTALLY_ORDERED_SET_ELEMENTS = TotallyOrderedSetElementsCategory()
    return _TOTALLY_ORDERED_SET_ELEMENTS


class TotallyOrderedSetObject(MathematicalObject):
    """A poset with a chosen total-order enumeration."""

    def __init__(
        self,
        *,
        category: TotallyOrderedSetsCategory,
        poset: PosetObject,
        element_at: PosetEnumeration,
        position_of: PosetPosition,
        finite_enumeration: tuple[PosetElement, ...] | None,
    ) -> None:
        self._poset = poset
        self._element_at = element_at
        self._position_of = position_of
        self._finite_enumeration = finite_enumeration
        self._elements: dict[int, TotallyOrderedSetElement] = {}
        super().__init__(category=category)

    def _poset_implementation(self) -> PosetObject:
        return self._poset

    def element(self, poset_element: PosetElement) -> TotallyOrderedSetElement:
        assert poset_element.ambient_poset() is self._poset
        key = id(poset_element)
        cached = self._elements.get(key)
        if cached is None:
            cached = TotallyOrderedSets().ElementType(
                ambient_object=self,
                poset_element=poset_element,
            )
            self._elements[key] = cached
        return cached

    def _membership(self, member: TotallyOrderedSetElement) -> Decision:
        assert TotallyOrderedSetElements().contains_total_order_element(member)
        return member.ambient_total_order() is self

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and TotallyOrderedSetElements().contains_total_order_element(value) and self._membership(value) is True

    def __iter__(self) -> Iterator[TotallyOrderedSetElement]:
        return iter(self.element(member) for member in self._poset)

    def __getitem__(self, position: int) -> TotallyOrderedSetElement:
        assert position >= 0
        member = self._element_at(position)
        assert self._poset._membership(member) is True
        return self.element(member)

    def position(self, member: TotallyOrderedSetElement) -> int:
        assert self._membership(member) is True
        position = self._position_of(member._poset_implementation())
        assert position >= 0
        assert self[position] == member
        return position

    def rank(self, member: TotallyOrderedSetElement) -> int:
        return self.position(member)

    def unrank(self, position: int) -> TotallyOrderedSetElement:
        return self[position]

    def enumeration_injection(self) -> Arrow:
        def position_of_set_element(member: SetElement) -> int:
            return self._position_of(self._poset.element(member))

        return EnumerationInjection(
            self._poset._set_implementation(),
            position_of_set_element,
        )

    def __repr__(self) -> str:
        if self._finite_enumeration is None:
            return f"Totally ordered {self._poset._set_implementation()}"
        return "[" + ", ".join(map(repr, self._finite_enumeration)) + "]"


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
    ) -> TotallyOrderedSetElement:
        category = self.base_category()
        assert is_totally_ordered_sets_category(category)
        source = self.domain()
        target = self.codomain()
        assert category.contains_total_order(source)
        assert category.contains_total_order(target)
        assert source._membership(member) is True
        image = self._poset_morphism(member._poset_implementation())
        return target.element(image)


class TotallyOrderedSetHomCategory(HomCategory):
    """The monotone maps between two totally ordered sets."""

    ObjectType = TotallyOrderedSetMorphism
    ElementType = TotallyOrderedSetMorphism

    def __call__(
        self,
        definition: TotalOrderMorphismDefinition | TotallyOrderedSetMorphism,
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

        existing = registered_value(definition)
        if existing is not None:
            assert self.contains_total_order_morphism(existing)
            return existing

        def poset_action(member: PosetElement) -> PosetElement:
            source_member = domain.element(member)
            if callable(definition):
                image = definition(source_member)
            else:
                image = definition[source_member]
            assert TotallyOrderedSetElements().contains_total_order_element(image)
            assert codomain._membership(image) is True
            return image._poset_implementation()

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
        assert self.contains_total_order_morphism(second)
        assert self.contains_total_order_morphism(first)
        underlying = PartiallyOrderedSets().compose(
            second._poset_implementation(),
            first._poset_implementation(),
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

    def __init__(self, total_orders: TotallyOrderedSetsCategory) -> None:
        self._total_orders = total_orders
        super().__init__(total_orders, PartiallyOrderedSets())

    def on_object(self, source: MathematicalObject) -> PosetObject:
        assert self._total_orders.contains_total_order(source)
        return source._poset_implementation()

    def on_morphism(self, morphism: Arrow) -> PosetMorphism:
        hom_category = morphism.hom_category()
        assert is_total_order_hom_category(hom_category)
        assert hom_category.contains_total_order_morphism(morphism)
        return morphism._poset_implementation()

    def on_element(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> PosetElement:
        assert self._total_orders.contains_total_order(source)
        assert TotallyOrderedSetElements().contains_total_order_element(element)
        assert element.ambient_total_order() is source
        return element._poset_implementation()

    def is_faithful(self) -> bool:
        return True


class FiniteTotallyOrderedSetObject(PullbackObject):
    """A represented finite total order."""

    def rank(self, member: TotallyOrderedSetElement) -> int:
        total_order = FiniteTotallyOrderedSets().first_projection()(self)
        assert TotallyOrderedSets().contains_total_order(total_order)
        return total_order.rank(member)


class FiniteTotallyOrderedSetsCategory(PullbackCategory):
    """The pullback of total orders and finite sets over sets."""

    def __init__(self, first: Functor, second: Functor) -> None:
        super().__init__(first, second, object_type=FiniteTotallyOrderedSetObject)

    def __repr__(self) -> str:
        return "Finite totally ordered sets"


class TotallyOrderedSetsCategory(Category):
    """Sets equipped with a chosen total order."""

    ObjectType = TotallyOrderedSetObject
    ElementType = TotallyOrderedSetElement

    def __init__(self) -> None:
        self._inclusion: TotalOrderInclusionFunctor | None = None
        self._finite_orders: FiniteTotallyOrderedSetsCategory | None = None
        super().__init__(
            object_type=TotallyOrderedSetObject,
            element_type=TotallyOrderedSetElement,
        )

    def __call__(
        self,
        poset: PosetObject,
        element_at: PosetEnumeration,
        position_of: PosetPosition,
        *,
        finite_enumeration: tuple[PosetElement, ...] | None = None,
    ) -> TotallyOrderedSetObject:
        if finite_enumeration is not None:
            assert len(finite_enumeration) == poset._set_implementation().cardinality()
        return self.ObjectType(
            category=self,
            poset=poset,
            element_at=element_at,
            position_of=position_of,
            finite_enumeration=finite_enumeration,
        )

    def _hom_category_type(self) -> type[HomCategory]:
        return TotallyOrderedSetHomCategory

    def inclusion(self) -> TotalOrderInclusionFunctor:
        if self._inclusion is None:
            self._inclusion = TotalOrderInclusionFunctor(self)
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
            self._finite_orders = FiniteTotallyOrderedSetsCategory(
                self.inclusion(),
                FinitePosets().first_projection(),
            )
        return self._finite_orders

    def __repr__(self) -> str:
        return "Totally ordered sets"


_PARTIALLY_ORDERED_SETS: PartiallyOrderedSetsCategory | None = None
_TOTALLY_ORDERED_SETS: TotallyOrderedSetsCategory | None = None
_ORDERED_FINITE_SETS: dict[
    tuple[SetElement, ...],
    PullbackObject,
] = {}


def PartiallyOrderedSets() -> PartiallyOrderedSetsCategory:
    global _PARTIALLY_ORDERED_SETS

    if _PARTIALLY_ORDERED_SETS is None:
        _PARTIALLY_ORDERED_SETS = PartiallyOrderedSetsCategory()
    return _PARTIALLY_ORDERED_SETS


def TotallyOrderedSets() -> TotallyOrderedSetsCategory:
    global _TOTALLY_ORDERED_SETS

    if _TOTALLY_ORDERED_SETS is None:
        _TOTALLY_ORDERED_SETS = TotallyOrderedSetsCategory()
    return _TOTALLY_ORDERED_SETS


def FinitePosets() -> FinitePosetsCategory:
    return PartiallyOrderedSets().Finite()


def FiniteTotallyOrderedSets() -> FiniteTotallyOrderedSetsCategory:
    return TotallyOrderedSets().Finite()


def Poset(
    members_and_relation: tuple[
        Iterable[SetElement],
        Callable[[SetElement, SetElement], Decision],
    ],
) -> PullbackObject:
    """Construct the finite poset defined by ``(members, leq)``."""
    members, relation = members_and_relation
    values = tuple(dict.fromkeys(members))
    underlying_set = FiniteSet(values)

    def transported_relation(left: PosetElement, right: PosetElement) -> Decision:
        forgetful_functor = PartiallyOrderedSets().forgetful_functor()
        left_value = forgetful_functor.on_element(left.ambient_poset(), left).value()
        right_value = forgetful_functor.on_element(right.ambient_poset(), right).value()
        assert SetElements().contains_set_element(left_value)
        assert SetElements().contains_set_element(right_value)
        return relation(left_value, right_value)

    poset = PartiallyOrderedSets()(underlying_set, transported_relation)
    return FinitePosets()(poset, underlying_set)


def ordered_set_owned_by(
    elements: Iterable[SetElement],
) -> PullbackObject:
    enumeration = tuple(dict.fromkeys(elements))
    cached = _ORDERED_FINITE_SETS.get(enumeration)
    if cached is None:
        underlying_set = FiniteSet(enumeration)
        owned_enumeration = tuple(underlying_set.element(element) for element in enumeration)
        positions: dict[SetElement, int] = {element: index for index, element in enumerate(owned_enumeration)}

        def ordered_relation(left: PosetElement, right: PosetElement) -> bool:
            forgetful_functor = PartiallyOrderedSets().forgetful_functor()
            left_element = forgetful_functor.on_element(left.ambient_poset(), left)
            right_element = forgetful_functor.on_element(right.ambient_poset(), right)
            return positions[left_element] <= positions[right_element]

        poset = PartiallyOrderedSets()(
            underlying_set,
            ordered_relation,
        )
        poset_enumeration = tuple(poset.element(element) for element in owned_enumeration)

        def position_of(member: PosetElement) -> int:
            return positions[member._set_implementation()]

        total_order = TotallyOrderedSets()(
            poset,
            poset_enumeration.__getitem__,
            position_of,
            finite_enumeration=poset_enumeration,
        )
        finite_poset = FinitePosets()(poset, underlying_set)
        cached = FiniteTotallyOrderedSets()(total_order, finite_poset)
        _ORDERED_FINITE_SETS[enumeration] = cached
    return cached


def finite_ordered_set(
    elements: Iterable[SetElement],
) -> PullbackObject:
    return ordered_set_owned_by(elements)


class SimplexOrderIndexing:
    """The canonical total orders ``Delta[n]`` and ``Delta[aleph0]``."""

    def __init__(self) -> None:
        self._countable_simplex: TotallyOrderedSetObject | None = None

    def __getitem__(self, index: int | Cardinal) -> MathematicalObject:
        from sage_categories.theories.cardinals import is_cardinal
        from sage_categories.theories.ordinals import Ordinals, ordinal

        if is_cardinal(index):
            if index.is_finite() is True:
                maximum = index.finite_value()
            else:
                assert index.is_countably_infinite()
                if self._countable_simplex is None:
                    naturals = NaturalNumbers()

                    def natural_order(
                        left: PosetElement,
                        right: PosetElement,
                    ) -> bool:
                        forgetful_functor = PartiallyOrderedSets().forgetful_functor()
                        left_element = forgetful_functor.on_element(left.ambient_poset(), left)
                        right_element = forgetful_functor.on_element(right.ambient_poset(), right)
                        left_ordinal = left_element.value()
                        right_ordinal = right_element.value()
                        assert Ordinals().contains_ordinal(left_ordinal)
                        assert Ordinals().contains_ordinal(right_ordinal)
                        decision = Ordinals()._is_lequal(left_ordinal, right_ordinal)
                        assert decision is not UNKNOWN
                        return decision

                    poset = PartiallyOrderedSets()(naturals, natural_order)

                    def natural_element(position: int) -> PosetElement:
                        return poset.element(naturals[position])

                    def natural_position(member: PosetElement) -> int:
                        return naturals.position(member._set_implementation())

                    self._countable_simplex = TotallyOrderedSets()(
                        poset,
                        natural_element,
                        natural_position,
                    )
                return self._countable_simplex
        else:
            maximum = index
        assert maximum >= -1
        naturals = NaturalNumbers()
        return finite_ordered_set(naturals.element(ordinal(position)) for position in range(maximum + 1))

    def __repr__(self) -> str:
        return "Delta"


_SIMPLEX_ORDERS = SimplexOrderIndexing()


def SimplexOrders() -> SimplexOrderIndexing:
    return _SIMPLEX_ORDERS


def is_partially_ordered_sets_category(
    category: Category,
) -> TypeIs[PartiallyOrderedSetsCategory]:
    return category is PartiallyOrderedSets()


def is_totally_ordered_sets_category(
    category: Category,
) -> TypeIs[TotallyOrderedSetsCategory]:
    return category is TotallyOrderedSets()


def is_poset_hom_category(
    category: HomCategory,
) -> TypeIs[PosetHomCategory]:
    return category.base_category() is PartiallyOrderedSets() and category in PartiallyOrderedSets().HomCategory()


def is_total_order_hom_category(
    category: HomCategory,
) -> TypeIs[TotallyOrderedSetHomCategory]:
    return category.base_category() is TotallyOrderedSets() and category in TotallyOrderedSets().HomCategory()
