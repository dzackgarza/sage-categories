"""Full subcategories."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.abstract_categories.functors import (
    Functor,
    InclusionFunctor,
    ConcreteFunctor,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
)
from sage_categories.category import Category
from sage_categories.types import (
    Arrow,
    Decision,
    MathematicalElement,
    MathematicalObject,
    Unknown,
    registered_element,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.assumptions import AppliedProperty

type ObjectPredicate = Callable[[MathematicalObject], Decision]


class FullSubcategoryObject(MathematicalObject):
    """The local object implementation of a full subcategory."""

    def __contains__(self, candidate: Any) -> Decision:
        element = registered_element(candidate)
        return element is not None and element.ambient_object() is self


class FullSubcategoryElement(MathematicalElement):
    """The local element implementation of a full subcategory."""


class FullSubcategoryArrow(Arrow):
    """The local arrow implementation of a full subcategory."""

class FullSubcategoryHomCategory(HomCategory):
    """The ambient arrows between two objects of a full subcategory."""

    ObjectType = FullSubcategoryArrow
    ElementType = FullSubcategoryArrow

    def __init__(
        self,
        *,
        domain: MathematicalObject,
        codomain: MathematicalObject,
        hom_category: HomCategoryFamily,
    ) -> None:
        self._ambient_inclusion: ConcreteFunctor | None = None
        super().__init__(
            domain=domain,
            codomain=codomain,
            hom_category=hom_category,
        )

    def full_subcategory(self) -> FullSubcategory:
        category = self.base_category()
        assert is_full_subcategory(category)
        return category

    def ambient_hom_category(self) -> HomCategory:
        category = self.full_subcategory()
        inclusion = category.inclusion()
        return category.ambient_category().Hom(
            inclusion.on_object(self.domain()),
            inclusion.on_object(self.codomain()),
        )

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        if value is None:
            return False
        category = self.full_subcategory()
        if not category.contains_arrow(value):
            return False
        ambient = category.ambient_category()
        if value.base_category() is ambient:
            ambient_candidate = value
        elif value.base_category().is_subcategory(ambient):
            from sage_categories.compiler import category_compiler

            route = category_compiler().implementation_route(
                value.base_category(),
                ambient,
            )
            ambient_candidate = value._morphism_image_along(route)
        else:
            return False
        return ambient_candidate in self.ambient_hom_category()

    def __call__(self, arrow: Arrow) -> Arrow:
        assert arrow in self
        ambient = self.full_subcategory().ambient_category()
        if arrow.base_category() is ambient:
            ambient_arrow = arrow
        else:
            from sage_categories.compiler import category_compiler

            route = category_compiler().implementation_route(
                arrow.base_category(),
                ambient,
            )
            ambient_arrow = arrow._morphism_image_along(route)
        return self.full_subcategory()._refine_arrow(self, ambient_arrow)

    def identity(self) -> Arrow:
        assert self.domain() is self.codomain()
        inclusion = self.full_subcategory().inclusion()
        ambient_domain = inclusion.on_object(self.domain())
        return self(inclusion.codomain().identity(ambient_domain))

    def compose(self, second: Arrow, first: Arrow) -> Arrow:
        assert first in self
        assert second in self
        ambient_category = self.full_subcategory().ambient_category()
        return self(
            ambient_category.compose(
                second._ambient_implementation(),
                first._ambient_implementation(),
            )
        )

    def structure_functors(self) -> tuple[Functor, ...]:
        if self._ambient_inclusion is None:
            self._ambient_inclusion = InclusionFunctor(
                self,
                self.ambient_hom_category(),
            )
        return (self._ambient_inclusion,)


class FullSubcategoryHomCategoryFamily(HomCategoryFamily):
    """The hom categories of one full property subcategory."""

    ObjectType: type[FullSubcategoryHomCategory] = FullSubcategoryHomCategory

    def __init__(self, base_category: FullSubcategory) -> None:
        self._full_hom_categories: dict[
            tuple[int, int],
            FullSubcategoryHomCategory,
        ] = {}
        super().__init__(
            base_category,
            hom_category_type=FullSubcategoryHomCategory,
        )

    def Of(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> FullSubcategoryHomCategory:
        base = self.base_category()
        assert domain in base
        assert codomain in base
        key = id(domain), id(codomain)
        cached = self._full_hom_categories.get(key)
        if cached is None:
            cached = self.ObjectType(
                domain=domain,
                codomain=codomain,
                hom_category=self,
            )
            self._full_hom_categories[key] = cached
        return cached


class FullSubcategory(Category):
    """The full subcategory on objects satisfying one predicate."""

    ObjectType: type[MathematicalObject] = FullSubcategoryObject
    ElementType: type[MathematicalElement] = FullSubcategoryElement
    ArrowType: type[Arrow] = FullSubcategoryArrow

    def __init__(
        self,
        ambient_category: Category,
        predicate: ObjectPredicate,
        *,
        name: str,
    ) -> None:
        self._ambient_category = ambient_category
        self._name = name
        self._inclusion: InclusionFunctor | None = None
        self._full_hom_category_family: FullSubcategoryHomCategoryFamily | None = None
        super().__init__(
            object_type=self.ObjectType,
            element_type=self.ElementType,
            arrow_type=self.ArrowType,
            category=FullSubcategoryCategoryObjects(),
        )
        from sage_categories.compiler import category_compiler

        category_compiler().register_object_property(
            ambient_category,
            self,
            predicate,
        )

    def ambient_category(self) -> Category:
        return self._ambient_category

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        if value is None:
            return False
        category = value.category()
        return category is self or category.is_subcategory(self)

    def __call__(self, ambient: MathematicalObject) -> MathematicalObject:
        """Construct ``ambient`` in this property category."""
        assert self.is_subcategory(ambient.category()) or ambient in self._ambient_category
        return self._refine_object(ambient)

    def predicate(self, candidate: MathematicalObject) -> AppliedProperty:
        """Apply this category's defining predicate to ``candidate``."""
        from sage_categories.assumptions import AppliedProperty

        assert self.is_subcategory(candidate.category()) or candidate in self._ambient_category
        return AppliedProperty(self, candidate)

    def _refine_object(self, ambient: MathematicalObject) -> MathematicalObject:
        from sage_categories.compiler import category_compiler

        if ambient.category() is self:
            assert ambient in self
            return ambient
        refined = category_compiler().refine_object(self, ambient)
        assert refined in self
        return refined

    def _refine_element(
        self,
        source: MathematicalObject,
        ambient: MathematicalElement,
    ) -> MathematicalElement:
        from sage_categories.compiler import category_compiler

        assert source in self
        inclusion = self.inclusion()
        ambient_source = inclusion.on_object(source)
        assert ambient.ambient_object() is ambient_source
        return category_compiler().refine_element(self, source, ambient)

    def _refine_arrow(self, hom_category: HomCategory, ambient: Arrow) -> Arrow:
        from sage_categories.compiler import category_compiler

        return category_compiler().refine_arrow(self, hom_category, ambient)

    def contains_arrow(self, candidate: MathematicalObject) -> TypeIs[Arrow]:
        if not self._ambient_category.contains_arrow(candidate):
            return False
        return candidate.domain() in self and candidate.codomain() in self

    def _hom_category_type(self) -> type[HomCategory]:
        return FullSubcategoryHomCategory

    def HomCategory(self) -> FullSubcategoryHomCategoryFamily:
        if self._full_hom_category_family is None:
            self._full_hom_category_family = FullSubcategoryHomCategoryFamily(self)
            self._full_hom_category_family.ElementType = self._compiled_arrow_type
        return self._full_hom_category_family

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> FullSubcategoryHomCategory:
        return self.HomCategory().Of(domain, codomain)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (self.inclusion(),)

    def inclusion(self) -> InclusionFunctor:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(self, self._ambient_category)
        return self._inclusion

    def _products_of_category(
        self,
        functor: Functor,
    ) -> Category:
        return self._ambient_category._products_of_category(functor)

    def _coproducts_of_category(
        self,
        functor: Functor,
    ) -> Category:
        return self._ambient_category._coproducts_of_category(functor)

    def _limits_of_category(
        self,
        functor: Functor,
    ) -> Category:
        return self._ambient_category._limits_of_category(functor)

    def _colimits_of_category(
        self,
        functor: Functor,
    ) -> Category:
        return self._ambient_category._colimits_of_category(functor)

    def __repr__(self) -> str:
        return self._name


class FullSubcategoryObjects(Category):
    """The represented category of full subcategories."""

    def __init__(self) -> None:
        super().__init__(object_type=FullSubcategory)


_FULL_SUBCATEGORIES = FullSubcategoryObjects()


def FullSubcategoryCategoryObjects() -> FullSubcategoryObjects:
    return _FULL_SUBCATEGORIES


def is_full_subcategory(category: Category) -> TypeIs[FullSubcategory]:
    return category in FullSubcategoryCategoryObjects()
