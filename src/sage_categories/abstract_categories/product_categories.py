"""Product categories."""

from __future__ import annotations

from typing import TypeIs

from sage_categories.abstract_categories.functors import (
    Functor,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
)
from sage_categories.abstract_categories.opposite_categories import BinaryProjectionSide
from sage_categories.category import Category
from sage_categories.values import (
    Arrow,
    CategoryElement,
    MathematicalObject,
)


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
    ) -> ProductArrow:
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
        assert is_product_arrow(second)
        assert is_product_arrow(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
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
        self._pairs: dict[tuple[int, int], CategoryPair] = {}
        self._first_projection: ProductProjectionFunctor | None = None
        self._second_projection: ProductProjectionFunctor | None = None
        super().__init__(
            object_type=CategoryPair,
            element_type=CategoryElement,
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
        assert first in self._first_category
        assert second in self._second_category
        key = id(first), id(second)
        cached = self._pairs.get(key)
        if cached is None:
            cached = self.ObjectType(category=self, first=first, second=second)
            self._pairs[key] = cached
        return cached

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

    def first_projection(self) -> ProductProjectionFunctor:
        if self._first_projection is None:
            self._first_projection = ProductProjectionFunctor(
                self,
                side=BinaryProjectionSide.FIRST,
            )
        return self._first_projection

    def second_projection(self) -> ProductProjectionFunctor:
        if self._second_projection is None:
            self._second_projection = ProductProjectionFunctor(
                self,
                side=BinaryProjectionSide.SECOND,
            )
        return self._second_projection

    def pair_functor(self, first: Functor, second: Functor) -> PairFunctor:
        return PairFunctor(self, first, second)

    def __repr__(self) -> str:
        return f"{self._first_category} x {self._second_category}"


class ProductProjectionFunctor(Functor):
    """One projection from a binary product category."""

    def __init__(
        self,
        product: ProductCategory,
        *,
        side: BinaryProjectionSide,
    ) -> None:
        self._product = product
        self._side = side
        codomain = side.select(
            product.first_category(),
            product.second_category(),
        )
        super().__init__(product, codomain)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._product.contains_pair(source)
        return self._side.select(source.first(), source.second())

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert is_product_arrow(morphism)
        return self._side.select(morphism.first(), morphism.second())


class PairFunctor(Functor):
    """The functor into a product induced by two functors."""

    def __init__(
        self,
        product: ProductCategory,
        first: Functor,
        second: Functor,
    ) -> None:
        assert first.domain() is second.domain()
        assert first.codomain() is product.first_category()
        assert second.codomain() is product.second_category()
        self._product = product
        self._first = first
        self._second = second
        super().__init__(first.domain(), product)

    def _object_image(self, source: MathematicalObject) -> CategoryPair:
        return self._product(self._first(source), self._second(source))

    def _morphism_image(self, morphism: Arrow) -> ProductArrow:
        source = self.on_object(morphism.domain())
        target = self.on_object(morphism.codomain())
        hom_category = self._product.Hom(source, target)
        assert is_product_hom_category(hom_category)
        first = self._first(morphism)
        second = self._second(morphism)
        assert self._first.codomain().contains_arrow(first)
        assert self._second.codomain().contains_arrow(second)
        return hom_category(first, second)


class ProductCategoryObjects(Category):
    """The category of binary product-category objects in ``Cat``."""

    def __init__(self) -> None:
        super().__init__(object_type=ProductCategory)


_PRODUCT_CATEGORIES = ProductCategoryObjects()


def ProductCategories() -> ProductCategoryObjects:
    return _PRODUCT_CATEGORIES


def is_product_category(category: Category) -> TypeIs[ProductCategory]:
    return category in ProductCategories()


def is_product_arrow(arrow: Arrow) -> TypeIs[ProductArrow]:
    return is_product_category(arrow.hom_category().base_category()) and arrow in arrow.hom_category().base_category().ArrowCategory()


def is_product_hom_category(
    hom_category: HomCategory,
) -> TypeIs[ProductHomCategory]:
    product = hom_category.base_category()
    return is_product_category(product) and hom_category is product.Hom(
        hom_category.domain(),
        hom_category.codomain(),
    )
