"""Opposite categories and binary products of categories.

The representations follow the research preamble and the standard
constructions in Mathlib's category-theory library.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeIs

from sage_categories.abstract_categories.functors import (
    InclusionFunctor,
    StructuralFunctor,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
)
from sage_categories.category import Category
from sage_categories.values import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
    MembershipInput,
    registered_value,
)

type ObjectPredicate = Callable[[MathematicalObject], bool]


class OppositeArrow(Arrow):
    """An arrow of an opposite category."""

    def __init__(self, *, hom_category: HomCategory, underlying_arrow: Arrow) -> None:
        opposite = hom_category.base_category()
        assert is_opposite_category(opposite)
        assert underlying_arrow in opposite.base_category().Hom(
            hom_category.codomain(),
            hom_category.domain(),
        )
        self._underlying_arrow = underlying_arrow
        super().__init__(hom_category=hom_category)

    def underlying_arrow(self) -> Arrow:
        return self._underlying_arrow


class OppositeHomCategory(HomCategory):
    """Arrows of an opposite category."""

    ObjectType = OppositeArrow
    ElementType = OppositeArrow

    def __call__(self, underlying_arrow: Arrow) -> OppositeArrow:
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> OppositeArrow:
        assert value is None
        assert self.domain() is self.codomain()
        opposite = self.base_category()
        assert is_opposite_category(opposite)
        return self(opposite.base_category().identity(self.domain()))

    def compose(self, second: Arrow, first: Arrow) -> OppositeArrow:
        assert self.contains_opposite_arrow(second)
        assert self.contains_opposite_arrow(first)
        assert first.codomain() is second.domain()
        opposite = self.base_category()
        assert is_opposite_category(opposite)
        return self(
            opposite.base_category().compose(
                first.underlying_arrow(),
                second.underlying_arrow(),
            )
        )

    def contains_opposite_arrow(self, arrow: Arrow) -> TypeIs[OppositeArrow]:
        return arrow in self


class OppositeCategory(Category):
    """The opposite category ``C^op``."""

    def __init__(self, base_category: Category) -> None:
        self._base_category = base_category
        super().__init__(
            object_type=base_category.ObjectType,
            element_type=base_category.ElementType,
            category=OppositeCategories(),
        )

    def base_category(self) -> Category:
        return self._base_category

    def __contains__(self, candidate: MembershipInput) -> bool:
        return candidate in self._base_category

    def _hom_category_type(self) -> type[HomCategory]:
        return OppositeHomCategory

    def OppositeCategory(self) -> Category:
        return self._base_category

    def __repr__(self) -> str:
        return f"{self._base_category}^op"


class CategoryPair(MathematicalObject):
    """An object of a binary product category."""

    def __init__(
        self,
        *,
        category: ProductCategory,
        first: MathematicalObject,
        second: MathematicalObject,
    ) -> None:
        assert first in category.first_category()
        assert second in category.second_category()
        self._first = first
        self._second = second
        super().__init__(category=category)

    def first(self) -> MathematicalObject:
        return self._first

    def second(self) -> MathematicalObject:
        return self._second

    def __repr__(self) -> str:
        return f"({self._first}, {self._second})"


class ProductArrow(Arrow):
    """A pair of arrows in a product category."""

    def __init__(
        self,
        *,
        hom_category: HomCategory,
        first: Arrow,
        second: Arrow,
    ) -> None:
        product = hom_category.base_category()
        assert is_product_category(product)
        domain = hom_category.domain()
        codomain = hom_category.codomain()
        assert product.contains_pair(domain)
        assert product.contains_pair(codomain)
        assert first in product.first_category().Hom(
            domain.first(),
            codomain.first(),
        )
        assert second in product.second_category().Hom(
            domain.second(),
            codomain.second(),
        )
        self._first = first
        self._second = second
        super().__init__(hom_category=hom_category)

    def first(self) -> Arrow:
        return self._first

    def second(self) -> Arrow:
        return self._second


class ProductHomCategory(HomCategory):
    """A hom category in a binary product category."""

    ObjectType = ProductArrow
    ElementType = ProductArrow

    def __call__(self, first: Arrow, second: Arrow) -> ProductArrow:
        return self.ObjectType(hom_category=self, first=first, second=second)

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> ProductArrow:
        assert value is None
        assert self.domain() is self.codomain()
        product = self.base_category()
        assert is_product_category(product)
        domain = self.domain()
        assert product.contains_pair(domain)
        return self(
            product.first_category().identity(domain.first()),
            product.second_category().identity(domain.second()),
        )

    def compose(self, second: Arrow, first: Arrow) -> ProductArrow:
        assert self.contains_product_arrow(second)
        assert self.contains_product_arrow(first)
        assert first.codomain() is second.domain()
        product = self.base_category()
        assert is_product_category(product)
        return self(
            product.first_category().compose(second.first(), first.first()),
            product.second_category().compose(second.second(), first.second()),
        )

    def contains_product_arrow(self, arrow: Arrow) -> TypeIs[ProductArrow]:
        return arrow in self


class ProductCategory(Category):
    """The binary product category ``C x D``."""

    ObjectType = CategoryPair

    def __init__(self, first_category: Category, second_category: Category) -> None:
        self._first_category = first_category
        self._second_category = second_category
        super().__init__(
            object_type=CategoryPair,
            element_type=MathematicalElement,
            category=ProductCategories(),
        )

    def first_category(self) -> Category:
        return self._first_category

    def second_category(self) -> Category:
        return self._second_category

    def pair(
        self,
        first: MathematicalObject,
        second: MathematicalObject,
    ) -> CategoryPair:
        return self.ObjectType(category=self, first=first, second=second)

    def contains_pair(self, candidate: MathematicalObject) -> TypeIs[CategoryPair]:
        return candidate in self

    def __call__(
        self,
        first: MathematicalObject,
        second: MathematicalObject,
    ) -> CategoryPair:
        return self.pair(first, second)

    def _hom_category_type(self) -> type[HomCategory]:
        return ProductHomCategory

    def __repr__(self) -> str:
        return f"{self._first_category} x {self._second_category}"


class FullSubcategoryHomCategory(HomCategory):
    """The ambient arrows between two objects of a full subcategory."""

    def __init__(
        self,
        *,
        domain: MathematicalObject,
        codomain: MathematicalObject,
        hom_category: HomCategoryFamily,
    ) -> None:
        self._ambient_inclusion: StructuralFunctor | None = None
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
        return category.ambient_category().Hom(self.domain(), self.codomain())

    def __contains__(self, candidate: MembershipInput) -> bool:
        return candidate in self.ambient_hom_category()

    def __call__(self, arrow: Arrow) -> Arrow:
        assert arrow in self
        return arrow

    def identity(self, value: MathematicalObject | None = None) -> Arrow:
        assert value is None
        assert self.domain() is self.codomain()
        return self.ambient_hom_category().identity()

    def compose(self, second: Arrow, first: Arrow) -> Arrow:
        assert first in self.full_subcategory().ArrowCategory()
        assert second in self.full_subcategory().ArrowCategory()
        return self.full_subcategory().ambient_category().compose(second, first)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._ambient_inclusion is None:
            self._ambient_inclusion = InclusionFunctor(
                self,
                self.ambient_hom_category(),
            )
        return (self._ambient_inclusion,)


class FullSubcategory(Category):
    """The full subcategory on objects satisfying one predicate."""

    def __init__(
        self,
        ambient_category: Category,
        predicate: ObjectPredicate,
        *,
        name: str,
    ) -> None:
        self._ambient_category = ambient_category
        self._predicate = predicate
        self._name = name
        self._inclusion: InclusionFunctor | None = None
        super().__init__(
            object_type=ambient_category.ObjectType,
            element_type=ambient_category.ElementType,
            category=FullSubcategoryCategoryObjects(),
        )

    def ambient_category(self) -> Category:
        return self._ambient_category

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        return value is not None and value in self._ambient_category and self._predicate(value)

    def contains_arrow(self, candidate: MathematicalObject) -> TypeIs[Arrow]:
        if not self._ambient_category.contains_arrow(candidate):
            return False
        return candidate.domain() in self and candidate.codomain() in self

    def _hom_category_type(self) -> type[HomCategory]:
        return FullSubcategoryHomCategory

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(self, self._ambient_category)
        return (self._inclusion,)

    def __repr__(self) -> str:
        return self._name


class OppositeCategoryObjects(Category):
    """The category of opposite-category objects in ``Cat``."""

    def __init__(self) -> None:
        super().__init__(object_type=OppositeCategory)


class ProductCategoryObjects(Category):
    """The category of binary product-category objects in ``Cat``."""

    def __init__(self) -> None:
        super().__init__(object_type=ProductCategory)


class FullSubcategoryObjects(Category):
    """The represented category of full subcategories."""

    def __init__(self) -> None:
        super().__init__(object_type=FullSubcategory)


_OPPOSITE_CATEGORIES = OppositeCategoryObjects()
_PRODUCT_CATEGORIES = ProductCategoryObjects()
_FULL_SUBCATEGORIES = FullSubcategoryObjects()


def OppositeCategories() -> OppositeCategoryObjects:
    return _OPPOSITE_CATEGORIES


def ProductCategories() -> ProductCategoryObjects:
    return _PRODUCT_CATEGORIES


def FullSubcategoryCategoryObjects() -> FullSubcategoryObjects:
    return _FULL_SUBCATEGORIES


def is_opposite_category(category: Category) -> TypeIs[OppositeCategory]:
    return category in OppositeCategories()


def is_product_category(category: Category) -> TypeIs[ProductCategory]:
    return category in ProductCategories()


def is_full_subcategory(category: Category) -> TypeIs[FullSubcategory]:
    return category in FullSubcategoryCategoryObjects()


def is_opposite_arrow(arrow: Arrow) -> TypeIs[OppositeArrow]:
    return is_opposite_category(arrow.hom_category().base_category()) and arrow in arrow.hom_category().base_category().ArrowCategory()


def is_product_arrow(arrow: Arrow) -> TypeIs[ProductArrow]:
    return is_product_category(arrow.hom_category().base_category()) and arrow in arrow.hom_category().base_category().ArrowCategory()
