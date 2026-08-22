"""Arrow categories and commuting squares.

The semantics are migrated from the research preamble's
``abstract_categories/arrow_categories.sage``.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeIs

from sage_categories.abstract_categories.functors import (
    InclusionFunctor,
    StructuralFunctor,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
    is_isomorphism_hom_category,
)
from sage_categories.category import Category
from sage_categories.values import (
    Arrow,
    MathematicalObject,
    MembershipInput,
    registered_value,
)


def common_category(objects: Iterable[MathematicalObject]) -> Category:
    """Return the most specific represented category containing all objects."""
    values = tuple(objects)
    assert values
    candidates: dict[int, Category] = {}

    def add_with_super_categories(category: Category) -> None:
        key = id(category)
        if key in candidates:
            return
        candidates[key] = category
        for super_category in category.super_categories():
            add_with_super_categories(super_category)

    for value in values:
        add_with_super_categories(value.category())
    common = tuple(category for category in candidates.values() if all(value in category for value in values))
    most_specific = tuple(
        category
        for category in common
        if not any(other is not category and other.is_subcategory(category) for other in common)
    )
    assert len(most_specific) == 1
    return most_specific[0]


class CommutingSquare(Arrow):
    """A morphism in ``Ar(C)``, represented by its two vertical arrows."""

    def __init__(
        self,
        *,
        hom_category: SquareHomCategory,
        left: Arrow,
        right: Arrow,
    ) -> None:
        source = hom_category.domain()
        target = hom_category.codomain()
        arrow_category = hom_category.base_category()
        assert arrow_category.contains_arrow(source)
        assert arrow_category.contains_arrow(target)
        category = arrow_category.base_category()
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

    ObjectType = CommutingSquare
    ElementType = CommutingSquare

    def __init__(
        self,
        *,
        domain: MathematicalObject,
        codomain: MathematicalObject,
        hom_category: ArrowHomCategoryFamily,
    ) -> None:
        self._square_family = hom_category
        super().__init__(
            domain=domain,
            codomain=codomain,
            hom_category=hom_category,
        )

    def base_category(self) -> ArrowCategory:
        return self._square_family.base_category()

    def __call__(self, left: Arrow, right: Arrow) -> CommutingSquare:
        return self.ObjectType(hom_category=self, left=left, right=right)

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> CommutingSquare:
        assert value is None
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
        self._square_hom_family: ArrowHomCategoryFamily | None = None
        super().__init__(object_type=base_category.ArrowType)

    def base_category(self) -> Category:
        """Return ``C`` from ``Ar(C)``."""
        return self._base_category

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        return value is not None and self._base_category.contains_arrow(value)

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

    def HomCategory(self) -> ArrowHomCategoryFamily:
        """Return the category of square categories in ``Ar(C)``."""
        if self._square_hom_family is None:
            self._square_hom_family = ArrowHomCategoryFamily(self)
        return self._square_hom_family

    def __repr__(self) -> str:
        return f"Ar({self._base_category})"


class ArrowHomCategoryFamily(HomCategoryFamily):
    """The hom-category family whose objects contain commuting squares."""

    ObjectType = SquareHomCategory

    def __init__(self, base_category: ArrowCategory) -> None:
        self._square_base_category = base_category
        super().__init__(base_category, hom_category_type=SquareHomCategory)

    def base_category(self) -> ArrowCategory:
        return self._square_base_category


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
        return value.hom_category() in self._base_category.MonoCategory() or (value.hom_category() in self._base_category.IsoCategory())

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
        return value.hom_category() in self._base_category.EpiCategory() or (value.hom_category() in self._base_category.IsoCategory())

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
        return category is self._base_category.EpimorphismArrowCategory() or super().is_subcategory(category)


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
        return category is self._base_category.EndArrowCategory() or super().is_subcategory(category)


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
            category=WideSubcategoryCategoryObjects(),
        )

    def base_category(self) -> Category:
        return self._base_category

    def arrows(self) -> Category:
        return self._arrows

    def __contains__(self, candidate: MembershipInput) -> bool:
        return candidate in self._base_category

    def contains_arrow(self, candidate: MathematicalObject) -> TypeIs[Arrow]:
        if not self._base_category.contains_arrow(candidate):
            return False
        return self.admits(candidate)

    def admits(self, arrow: Arrow) -> bool:
        return arrow in self._arrows

    def arrow(self, arrow: Arrow) -> Arrow:
        assert self.admits(arrow)
        return arrow

    def identity_arrow(self, value: MathematicalObject) -> Arrow:
        if self._arrows is self._base_category.EndArrowCategory():
            return self._base_category.End(value).identity()
        if self._arrows is self._base_category.MonomorphismArrowCategory():
            return self._base_category.Mono(value, value).identity()
        if self._arrows is self._base_category.EpimorphismArrowCategory():
            return self._base_category.Epi(value, value).identity()
        if self._arrows is self._base_category.IsomorphismArrowCategory():
            return self._base_category.Iso(value, value).identity()
        if self._arrows is self._base_category.AutomorphismArrowCategory():
            return self._base_category.Aut(value).identity()
        identity = self._base_category.identity(value)
        assert self.admits(identity)
        return identity

    def compose_arrows(self, second: Arrow, first: Arrow) -> Arrow:
        domain = first.domain()
        codomain = second.codomain()
        if self._arrows is self._base_category.EndArrowCategory():
            return self._base_category.End(domain).compose(second, first)
        if self._arrows is self._base_category.MonomorphismArrowCategory():
            return self._base_category.Mono(domain, codomain).compose(second, first)
        if self._arrows is self._base_category.EpimorphismArrowCategory():
            return self._base_category.Epi(domain, codomain).compose(second, first)
        if self._arrows is self._base_category.IsomorphismArrowCategory():
            return self._base_category.Iso(domain, codomain).compose(second, first)
        if self._arrows is self._base_category.AutomorphismArrowCategory():
            return self._base_category.Aut(domain).compose(second, first)
        composite = self._base_category.compose(second, first)
        assert self.admits(composite)
        return composite

    def _hom_category_type(self) -> type[HomCategory]:
        return WideHomCategory

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(self, self._base_category)
        return (self._inclusion,)


class WideHomCategory(HomCategory):
    """The admitted arrows between two objects of a wide subcategory."""

    def wide_subcategory(self) -> WideSubcategory:
        wide = self.base_category()
        assert is_wide_subcategory(wide)
        return wide

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        if value is None:
            return False
        wide = self.wide_subcategory()
        if not wide.base_category().contains_arrow(value):
            return False
        return value in wide.base_category().Hom(self.domain(), self.codomain()) and wide.admits(value)

    def __call__(self, arrow: Arrow) -> Arrow:
        assert arrow in self
        return arrow

    def identity(self, value: MathematicalObject | None = None) -> Arrow:
        assert value is None
        assert self.domain() is self.codomain()
        wide = self.wide_subcategory()
        identity = wide.identity_arrow(self.domain())
        assert identity in self
        return identity

    def compose(self, second: Arrow, first: Arrow) -> Arrow:
        wide = self.wide_subcategory()
        composite = wide.compose_arrows(second, first)
        assert composite in self
        return composite


class WideSubcategoryObjects(Category):
    """The represented category of wide subcategories."""

    def __init__(self) -> None:
        super().__init__(object_type=WideSubcategory)


_WIDE_SUBCATEGORY_OBJECTS = WideSubcategoryObjects()


def WideSubcategoryCategoryObjects() -> WideSubcategoryObjects:
    return _WIDE_SUBCATEGORY_OBJECTS


def is_wide_subcategory(category: Category) -> TypeIs[WideSubcategory]:
    return category in _WIDE_SUBCATEGORY_OBJECTS


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
        isomorphisms = category.Aut(forward.domain())
    else:
        isomorphisms = category.Iso(forward.domain(), forward.codomain())
    assert is_isomorphism_hom_category(isomorphisms)
    return isomorphisms(forward, backward)
