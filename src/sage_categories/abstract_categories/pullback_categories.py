"""Pullback categories."""

from __future__ import annotations

from collections.abc import Callable

from enum import Enum

from typing import TYPE_CHECKING, Any, TypeIs, assert_never

from sage_categories.abstract_categories.functors import (
    Functor,
    InclusionFunctor,
    NaturalIsomorphism,
    StructuralFunctor,
    compose_functors,
)

from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
    Isomorphism,
    is_isomorphism,
)

from sage_categories.category import Category

from sage_categories.values import (
    Arrow,
    CategoryElement,
    MathematicalElement,
    MathematicalObject,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.abstract_categories.products import (
        CoconeObject,
        ConeObject,
        CoproductPresentation,
        ProductPresentation,
    )

from sage_categories.abstract_categories.opposite_categories import BinaryProjectionSide

class PullbackObject(MathematicalObject):
    """A compatible pair of objects in a strict pullback of categories."""

    def __init__(
        self,
        *,
        category: PullbackCategory,
        first: MathematicalObject,
        second: MathematicalObject,
    ) -> None:
        assert first in category.first_category()
        assert second in category.second_category()
        assert category.first_functor()(first) is category.second_functor()(second)
        self._first = first
        self._second = second
        super().__init__(category=category)

    def _first_implementation(self) -> MathematicalObject:
        return self._first

    def _second_implementation(self) -> MathematicalObject:
        return self._second

class PullbackElement(MathematicalElement):
    """A compatible pair of elements in a pullback object."""

    def __init__(
        self,
        *,
        category: PullbackCategory,
        ambient_object: PullbackObject,
        first: MathematicalElement,
        second: MathematicalElement,
    ) -> None:
        assert first.ambient_object() is ambient_object._first_implementation()
        assert second.ambient_object() is ambient_object._second_implementation()
        self._first = first
        self._second = second
        super().__init__(category=category, ambient_object=ambient_object)
        _PULLBACK_ELEMENTS[id(self)] = self

    def _first_implementation(self) -> MathematicalElement:
        return self._first

    def _second_implementation(self) -> MathematicalElement:
        return self._second

class PullbackArrow(Arrow):
    """A compatible pair of arrows in a pullback category."""

    def __init__(
        self,
        *,
        hom_category: HomCategory,
        first: Arrow,
        second: Arrow,
    ) -> None:
        pullback = hom_category.base_category()
        assert is_pullback_category(pullback)
        domain = hom_category.domain()
        codomain = hom_category.codomain()
        assert pullback.contains_pullback_object(domain)
        assert pullback.contains_pullback_object(codomain)
        assert first in pullback.first_category().Hom(
            domain._first_implementation(),
            codomain._first_implementation(),
        )
        assert second in pullback.second_category().Hom(
            domain._second_implementation(),
            codomain._second_implementation(),
        )
        common_first = pullback.first_functor()(first)
        common_second = pullback.second_functor()(second)
        assert pullback.common_category().contains_arrow(common_first)
        assert pullback.common_category().contains_arrow(common_second)
        assert common_first is common_second
        self._first = first
        self._second = second
        super().__init__(hom_category=hom_category)

    def _first_implementation(self) -> Arrow:
        return self._first

    def _second_implementation(self) -> Arrow:
        return self._second

class PullbackHomCategory(HomCategory):
    """Compatible pairs of arrows between pullback objects."""

    ObjectType = PullbackArrow
    ElementType = PullbackArrow

    def __call__(self, first: Arrow, second: Arrow) -> PullbackArrow:
        return self.ObjectType(
            hom_category=self,
            first=first,
            second=second,
        )

    def identity(self, value: MathematicalObject | None = None) -> PullbackArrow:
        assert value is None
        assert self.domain() is self.codomain()
        pullback = self.base_category()
        assert is_pullback_category(pullback)
        domain = self.domain()
        assert pullback.contains_pullback_object(domain)
        return self(
            pullback.first_category().identity(domain._first_implementation()),
            pullback.second_category().identity(domain._second_implementation()),
        )

    def compose(self, second: Arrow, first: Arrow) -> PullbackArrow:
        pullback = self.base_category()
        assert is_pullback_category(pullback)
        assert pullback.contains_pullback_arrow(second)
        assert pullback.contains_pullback_arrow(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        return self(
            pullback.first_category().compose(
                second._first_implementation(),
                first._first_implementation(),
            ),
            pullback.second_category().compose(
                second._second_implementation(),
                first._second_implementation(),
            ),
        )

    def contains_pullback_arrow(self, arrow: Arrow) -> TypeIs[PullbackArrow]:
        return arrow in self

class PullbackProjectionFunctor(StructuralFunctor):
    """One structural projection from a pullback category."""

    def __init__(
        self,
        pullback: PullbackCategory,
        *,
        side: BinaryProjectionSide,
    ) -> None:
        self._pullback = pullback
        self._side = side
        codomain = side.select(
            pullback.first_category(),
            pullback.second_category(),
        )
        super().__init__(pullback, codomain)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._pullback.contains_pullback_object(source)
        return self._side.select(
            source._first_implementation(),
            source._second_implementation(),
        )

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert self._pullback.contains_pullback_arrow(morphism)
        return self._side.select(
            morphism._first_implementation(),
            morphism._second_implementation(),
        )

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        assert self._pullback.contains_pullback_object(source)
        assert self._pullback.contains_pullback_element(element)
        return self._side.select(
            element._first_implementation(),
            element._second_implementation(),
        )

class PullbackMediatingFunctor(Functor):
    """The functor induced by a compatible pair of functors."""

    def __init__(
        self,
        pullback: PullbackCategory,
        first: Functor,
        second: Functor,
    ) -> None:
        assert first.domain() is second.domain()
        assert first.codomain() is pullback.first_category()
        assert second.codomain() is pullback.second_category()
        self._pullback = pullback
        self._first = first
        self._second = second
        super().__init__(first.domain(), pullback)

    def _object_image(self, source: MathematicalObject) -> PullbackObject:
        return self._pullback(self._first(source), self._second(source))

    def _morphism_image(self, morphism: Arrow) -> PullbackArrow:
        source = self.on_object(morphism.domain())
        target = self.on_object(morphism.codomain())
        hom_category = self._pullback.Hom(source, target)
        assert is_pullback_hom_category(hom_category)
        first = self._first(morphism)
        second = self._second(morphism)
        assert self._first.codomain().contains_arrow(first)
        assert self._second.codomain().contains_arrow(second)
        return hom_category(first, second)

class PullbackCategory(Category):
    """The strict pullback of two functors with one codomain."""

    ObjectType = PullbackObject
    ElementType = PullbackElement

    def __init__(
        self,
        first: Functor,
        second: Functor,
        *,
        object_type: type[PullbackObject] | None = None,
        element_type: type[PullbackElement] | None = None,
    ) -> None:
        assert first.codomain() is second.codomain()
        self._first_functor = first
        self._second_functor = second
        self._objects: dict[tuple[int, int], PullbackObject] = {}
        self._first_projection: PullbackProjectionFunctor | None = None
        self._second_projection: PullbackProjectionFunctor | None = None
        self._structural_coherence: Isomorphism | None = None
        super().__init__(
            object_type=object_type,
            element_type=element_type,
            category=PullbackCategories(),
        )

    def first_functor(self) -> Functor:
        return self._first_functor

    def second_functor(self) -> Functor:
        return self._second_functor

    def first_category(self) -> Category:
        return self._first_functor.domain()

    def second_category(self) -> Category:
        return self._second_functor.domain()

    def common_category(self) -> Category:
        return self._first_functor.codomain()

    def __call__(
        self,
        first: MathematicalObject,
        second: MathematicalObject,
    ) -> PullbackObject:
        key = id(first), id(second)
        cached = self._objects.get(key)
        if cached is None:
            cached = self.ObjectType(
                category=self,
                first=first,
                second=second,
            )
            self._objects[key] = cached
        return cached

    def element(
        self,
        source: PullbackObject,
        first: MathematicalElement,
        second: MathematicalElement,
    ) -> PullbackElement:
        return self.ElementType(
            category=self,
            ambient_object=source,
            first=first,
            second=second,
        )

    def contains_pullback_object(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[PullbackObject]:
        return candidate in self

    def contains_pullback_element(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[PullbackElement]:
        value = _PULLBACK_ELEMENTS.get(id(candidate))
        return value is candidate and candidate in self

    def contains_pullback_arrow(self, candidate: Arrow) -> TypeIs[PullbackArrow]:
        return candidate in self.ArrowCategory()

    def _hom_category_type(self) -> type[HomCategory]:
        return PullbackHomCategory

    def first_projection(self) -> PullbackProjectionFunctor:
        if self._first_projection is None:
            self._first_projection = PullbackProjectionFunctor(
                self,
                side=BinaryProjectionSide.FIRST,
            )
        return self._first_projection

    def second_projection(self) -> PullbackProjectionFunctor:
        if self._second_projection is None:
            self._second_projection = PullbackProjectionFunctor(
                self,
                side=BinaryProjectionSide.SECOND,
            )
        return self._second_projection

    def mediating_functor(
        self,
        first: Functor,
        second: Functor,
    ) -> PullbackMediatingFunctor:
        return PullbackMediatingFunctor(self, first, second)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return self.first_projection(), self.second_projection()

    def structural_coherences(self) -> tuple[Isomorphism, ...]:
        if self._structural_coherence is None:
            first = compose_functors(
                self.first_functor(),
                self.first_projection(),
            )
            second = compose_functors(
                self.second_functor(),
                self.second_projection(),
            )

            def component(source: MathematicalObject) -> Arrow:
                image = first(source)
                assert image is second(source)
                return self.common_category().identity(image)

            coherence = NaturalIsomorphism(
                first,
                second,
                component,
                component,
            )
            assert is_isomorphism(coherence)
            self._structural_coherence = coherence
        return (self._structural_coherence,)

    def __repr__(self) -> str:
        return f"{self.first_category()} x_{self.common_category()} {self.second_category()}"

class PullbackCategoryObjects(Category):
    """The category of strict pullback-category objects in ``Cat``."""

    def __init__(self) -> None:
        super().__init__(object_type=PullbackCategory)

_PULLBACK_CATEGORIES = PullbackCategoryObjects()

def PullbackCategories() -> PullbackCategoryObjects:
    return _PULLBACK_CATEGORIES

def is_pullback_category(category: Category) -> TypeIs[PullbackCategory]:
    return category in PullbackCategories()

def is_pullback_hom_category(
    hom_category: HomCategory,
) -> TypeIs[PullbackHomCategory]:
    pullback = hom_category.base_category()
    return is_pullback_category(pullback) and hom_category is pullback.Hom(
        hom_category.domain(),
        hom_category.codomain(),
    )
