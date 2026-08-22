"""Runtime values used by the owned categorical foundation.

The mathematical organization follows the abstract-category layer in
``dzack_research.preamble.categories.abstract_categories``. The runtime is
independent of Sage's category classes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import StructuralFunctor
    from sage_categories.category import Category
    from sage_categories.abstract_categories.hom_categories import HomCategory

type MembershipInput = Any


_VALUES: dict[int, MathematicalObject] = {}


def registered_value(candidate: MembershipInput) -> MathematicalObject | None:
    """Return the owned mathematical value represented by ``candidate``."""
    candidate_id = id(candidate)
    value = _VALUES.get(candidate_id)
    if value is not None and id(value) == candidate_id:
        return value
    return None


class MathematicalObject:
    """An object of a category, with cached structural-functor images."""

    def __init__(self, *, category: Category | None) -> None:
        self._category = category
        self._structural_images: dict[int, MathematicalObject] = {}
        if category is not None:
            self._structural_images[id(category)] = self
        _VALUES[id(self)] = self

    def category(self) -> Category:
        """Return the category in which this object was constructed."""
        assert self._category is not None
        return self._category

    def _belongs_to(self, category: Category) -> bool:
        if self._category is None:
            return False
        return self._category is category or self._category.is_subcategory(category)

    def _belongs_to_hom(self, hom_category: HomCategory) -> bool:
        return False

    def _is_arrow_in(self, category: Category) -> bool:
        return False

    def _image_along(
        self,
        route: tuple[StructuralFunctor, ...],
    ) -> MathematicalObject:
        value = self
        for functor in route:
            codomain = functor.codomain()
            key = id(codomain)
            cached = self._structural_images.get(key)
            if cached is not None:
                value = cached
                continue
            value = functor.on_object(value)
            assert value in codomain
            self._structural_images[key] = value
        return value


class MathematicalElement(MathematicalObject):
    """An element of a mathematical object."""

    def __init__(self, *, category: Category) -> None:
        super().__init__(category=category)


class Arrow(MathematicalElement):
    """An object of ``Ar(C)`` and an element of one hom category of ``C``."""

    def __init__(self, *, hom_category: HomCategory) -> None:
        self._hom_category = hom_category
        super().__init__(
            category=hom_category.base_category().ArrowCategory(),
        )

    def hom_category(self) -> HomCategory:
        """Return the hom category containing this arrow."""
        return self._hom_category

    def base_category(self) -> Category:
        """Return the category in which this arrow has its endpoints."""
        return self._hom_category.base_category()

    def domain(self) -> MathematicalObject:
        """Return the source object."""
        return self._hom_category.domain()

    def codomain(self) -> MathematicalObject:
        """Return the target object."""
        return self._hom_category.codomain()

    def source(self) -> MathematicalObject:
        """Return the source object."""
        return self.domain()

    def target(self) -> MathematicalObject:
        """Return the target object."""
        return self.codomain()

    def forward(self) -> Arrow:
        """Return the represented ordinary arrow."""
        return self

    def _belongs_to_hom(self, hom_category: HomCategory) -> bool:
        return self._hom_category is hom_category

    def _is_arrow_in(self, category: Category) -> bool:
        base = self.base_category()
        return base is category or base.is_subcategory(category)

    def __mul__(self, first: Arrow) -> Arrow:
        """Return this arrow after ``first``."""
        return self.base_category().compose(self, first)
