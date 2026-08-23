"""Thin categories."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, TypeIs

from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
)
from sage_categories.category import Category
from sage_categories.theories.poset_core import (
    PartiallyOrderedSets,
    PosetElement,
    PosetElements,
    PosetObject,
)
from sage_categories.theories.sets import (
    FiniteSet,
    SetElement,
    SetElements,
    SetObject,
    Sets,
)
from sage_categories.values import (
    UNKNOWN,
    Arrow,
    Decision,
    MathematicalObject,
    registered_value,
)


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

    def membership(self, member: SetElement) -> Decision:
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

    def membership(self, member: SetElement) -> Decision:
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
        return (
            PosetElements().contains_poset_element(candidate)
            and candidate.ambient_poset() is self._poset
        )

    def objects(self) -> ThinCategoryObjectSet:
        if self._objects is None:
            self._objects = ThinCategoryObjectSet(self)
        return self._objects

    def object_element(self, value: MathematicalObject) -> SetElement:
        assert PosetElements().contains_poset_element(value)
        return self.objects().element(value)

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
