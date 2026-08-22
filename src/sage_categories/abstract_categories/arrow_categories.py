"""Arrow categories and commuting squares.

The semantics are migrated from the research preamble's
``abstract_categories/arrow_categories.sage``.
"""

from __future__ import annotations

from typing import TypeIs

from sage_categories.abstract_categories.hom_categories import HomCategory
from sage_categories.category import Category
from sage_categories.values import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
    MembershipInput,
    registered_value,
)

from sage_categories.abstract_categories.functors import (
    InclusionFunctor,
    StructuralFunctor,
)


class CommutingSquare(Arrow):
    """A morphism in ``Ar(C)``, represented by its two vertical arrows."""

    def __init__(
        self,
        *,
        hom_category: HomCategory,
        left: Arrow,
        right: Arrow,
    ) -> None:
        source = hom_category.domain()
        target = hom_category.codomain()
        assert hom_category.base_category().contains_arrow(source)
        assert hom_category.base_category().contains_arrow(target)
        category = hom_category.base_category().base_category()
        assert left in category.ArrowCategory()
        assert right in category.ArrowCategory()
        assert left.domain() is source.domain()
        assert left.codomain() is target.domain()
        assert right.domain() is source.codomain()
        assert right.codomain() is target.codomain()
        self._left = left
        self._right = right
        super().__init__(hom_category=hom_category)

    def left(self) -> Arrow:
        """Return the domain-side arrow of the square."""
        return self._left

    def right(self) -> Arrow:
        """Return the codomain-side arrow of the square."""
        return self._right


class SquareHomCategory(HomCategory):
    """A category of commuting squares between two arrows."""

    ElementType = CommutingSquare

    def __call__(self, left: Arrow, right: Arrow) -> CommutingSquare:
        return self.ObjectType(hom_category=self, left=left, right=right)

    def identity(self) -> CommutingSquare:
        source = self.domain()
        assert source is self.codomain()
        assert self.base_category().contains_arrow(source)
        category = self.base_category().base_category()
        return self(
            category.identity(source.domain()),
            category.identity(source.codomain()),
        )

    def compose(self, second: Arrow, first: Arrow) -> CommutingSquare:
        assert self.base_category().contains_square(second)
        assert self.base_category().contains_square(first)
        assert first.codomain() is second.domain()
        category = self.base_category().base_category()
        return self(
            category.compose(second.left(), first.left()),
            category.compose(second.right(), first.right()),
        )


class ArrowCategory(Category):
    """``Ar(C)``: arrows of ``C`` as objects and commuting squares as arrows."""

    def __init__(self, base_category: Category) -> None:
        self._base_category = base_category
        super().__init__(object_type=base_category.ArrowType)

    def base_category(self) -> Category:
        """Return ``C`` from ``Ar(C)``."""
        return self._base_category

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        return value is not None and value._is_arrow_in(self._base_category)

    def contains_arrow(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[Arrow]:
        """Narrow an owned value by categorical arrow membership."""
        return candidate in self

    def contains_square(self, candidate: Arrow) -> TypeIs[CommutingSquare]:
        """Narrow an arrow by membership in an ``Ar(C)`` hom category."""
        return candidate in self.ArrowCategory()

    def __call__(self, arrow: Arrow) -> Arrow:
        assert arrow in self
        return arrow

    def _hom_category_type(self) -> type[HomCategory]:
        return SquareHomCategory

    def __repr__(self) -> str:
        return f"Ar({self._base_category})"


class EndArrowCategory(Category):
    """The full subcategory of ``Ar(C)`` on endomorphisms."""

    def __init__(self, base_category: Category) -> None:
        self._base_category = base_category
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=base_category.EndArrowType)

    def base_category(self) -> Category:
        return self._base_category

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        if value is None or not self._base_category.ArrowCategory().contains_arrow(value):
            return False
        return value.domain() is value.codomain()

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(
                self,
                self._base_category.ArrowCategory(),
            )
        return (self._inclusion,)


class MonomorphismArrowCategory(Category):
    """The subcategory of ``Ar(C)`` on declared monomorphisms."""

    def __init__(self, base_category: Category) -> None:
        self._base_category = base_category
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=base_category.MonoArrowType)

    def base_category(self) -> Category:
        return self._base_category

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        if value is None or not self._base_category.ArrowCategory().contains_arrow(value):
            return False
        return value.hom_category() in self._base_category.MonoCategory() or (
            value.hom_category() in self._base_category.IsoCategory()
        )

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(
                self,
                self._base_category.ArrowCategory(),
            )
        return (self._inclusion,)


class EpimorphismArrowCategory(Category):
    """The subcategory of ``Ar(C)`` on declared epimorphisms."""

    def __init__(self, base_category: Category) -> None:
        self._base_category = base_category
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=base_category.EpiArrowType)

    def base_category(self) -> Category:
        return self._base_category

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        if value is None or not self._base_category.ArrowCategory().contains_arrow(value):
            return False
        return value.hom_category() in self._base_category.EpiCategory() or (
            value.hom_category() in self._base_category.IsoCategory()
        )

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(
                self,
                self._base_category.ArrowCategory(),
            )
        return (self._inclusion,)


class IsomorphismArrowCategory(Category):
    """The subcategory of ``Ar(C)`` on declared isomorphisms."""

    def __init__(self, base_category: Category) -> None:
        self._base_category = base_category
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=base_category.IsoArrowType)

    def base_category(self) -> Category:
        return self._base_category

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        if value is None or not self._base_category.ArrowCategory().contains_arrow(value):
            return False
        return value.hom_category() in self._base_category.IsoCategory()

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(
                self,
                self._base_category.MonomorphismArrowCategory(),
            )
        return (self._inclusion,)

    def is_subcategory(self, category: Category) -> bool:
        return (
            category is self._base_category.EpimorphismArrowCategory()
            or super().is_subcategory(category)
        )


class AutomorphismArrowCategory(Category):
    """The full subcategory of ``Ar(C)`` on automorphisms."""

    def __init__(self, base_category: Category) -> None:
        self._base_category = base_category
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=base_category.AutArrowType)

    def base_category(self) -> Category:
        return self._base_category

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        if value is None or not self._base_category.ArrowCategory().contains_arrow(value):
            return False
        return value.hom_category() in self._base_category.AutCategory()

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(
                self,
                self._base_category.IsomorphismArrowCategory(),
            )
        return (self._inclusion,)

    def is_subcategory(self, category: Category) -> bool:
        return (
            category is self._base_category.EndArrowCategory()
            or super().is_subcategory(category)
        )


class WideSubcategory(Category):
    """All objects of a category with arrows restricted to one arrow category."""

    def __init__(self, base_category: Category, arrows: Category) -> None:
        assert arrows.is_subcategory(base_category.ArrowCategory())
        self._base_category = base_category
        self._arrows = arrows
        self._inclusion: InclusionFunctor | None = None
        super().__init__(
            object_type=base_category.ObjectType,
            element_type=base_category.ElementType,
        )

    def base_category(self) -> Category:
        return self._base_category

    def arrows(self) -> Category:
        return self._arrows

    def __contains__(self, candidate: MembershipInput) -> bool:
        return candidate in self._base_category

    def admits(self, arrow: Arrow) -> bool:
        return arrow in self._arrows

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(self, self._base_category)
        return (self._inclusion,)


def Core(base_category: Category) -> WideSubcategory:
    """Return the maximal subgroupoid of ``base_category``."""
    return WideSubcategory(
        base_category,
        base_category.IsomorphismArrowCategory(),
    )


def declare_isomorphism(forward: Arrow, backward: Arrow) -> Arrow:
    """Return the isomorphism represented by mutually inverse arrows."""
    assert backward.domain() is forward.codomain()
    assert backward.codomain() is forward.domain()
    category = forward.base_category()
    assert backward in category.ArrowCategory()
    if forward.domain() is forward.codomain():
        return category.Aut(forward.domain())(forward, backward)
    return category.Iso(forward.domain(), forward.codomain())(forward, backward)
