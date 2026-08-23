"""Opposite categories."""

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

class BinaryProjectionSide(Enum):
    """One factor of a binary categorical construction."""

    FIRST = "first"
    SECOND = "second"

    def select[Projected](
        self,
        first: Projected,
        second: Projected,
    ) -> Projected:
        match self:
            case BinaryProjectionSide.FIRST:
                return first
            case BinaryProjectionSide.SECOND:
                return second
            case _:
                assert_never(self)

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
        assert is_opposite_arrow(second)
        assert is_opposite_arrow(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
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

    def __contains__(self, candidate: Any) -> bool:
        return candidate in self._base_category

    def _hom_category_type(self) -> type[HomCategory]:
        return OppositeHomCategory

    def OppositeCategory(self) -> Category:
        return self._base_category

    def __repr__(self) -> str:
        return f"{self._base_category}^op"

class OppositeCategoryObjects(Category):
    """The category of opposite-category objects in ``Cat``."""

    def __init__(self) -> None:
        super().__init__(object_type=OppositeCategory)

_OPPOSITE_CATEGORIES = OppositeCategoryObjects()

def OppositeCategories() -> OppositeCategoryObjects:
    return _OPPOSITE_CATEGORIES

def is_opposite_category(category: Category) -> TypeIs[OppositeCategory]:
    return category in OppositeCategories()

def is_opposite_arrow(arrow: Arrow) -> TypeIs[OppositeArrow]:
    return is_opposite_category(arrow.hom_category().base_category()) and arrow in arrow.hom_category().base_category().ArrowCategory()

def is_opposite_hom_category(
    hom_category: HomCategory,
) -> TypeIs[OppositeHomCategory]:
    opposite = hom_category.base_category()
    return is_opposite_category(opposite) and hom_category is opposite.Hom(
        hom_category.domain(),
        hom_category.codomain(),
    )
