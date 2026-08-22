"""Slice, coslice, subobject, and covering-object categories."""

from __future__ import annotations

from typing import TypeIs

from sage_categories.abstract_categories.functors import (
    InclusionFunctor,
    StructuralFunctor,
)
from sage_categories.abstract_categories.hom_categories import HomCategory
from sage_categories.category import Category
from sage_categories.values import Arrow, MathematicalObject, MembershipInput


class SliceArrow(Arrow):
    """A commuting triangle in a slice or coslice category."""

    def __init__(
        self,
        *,
        hom_category: HomCategory,
        varying_arrow: Arrow,
    ) -> None:
        category = hom_category.base_category()
        assert is_slice_over(category) or is_coslice_under(category)
        self._varying_arrow = varying_arrow
        super().__init__(hom_category=hom_category)

    def varying_arrow(self) -> Arrow:
        return self._varying_arrow


class SliceHomCategory(HomCategory):
    """Commuting triangles over one fixed object."""

    ElementType = SliceArrow

    def __call__(self, left: Arrow) -> SliceArrow:
        category = self.base_category()
        assert is_slice_over(category)
        source = self.domain()
        target = self.codomain()
        assert category.contains_slice_object(source)
        assert category.contains_slice_object(target)
        assert left in category.ambient_category().Hom(
            source.domain(),
            target.domain(),
        )
        return self.ObjectType(hom_category=self, varying_arrow=left)

    def identity(self) -> SliceArrow:
        assert self.domain() is self.codomain()
        category = self.base_category()
        assert is_slice_over(category)
        assert category.contains_slice_object(self.domain())
        return self(category.ambient_category().identity(self.domain().domain()))

    def compose(self, second: Arrow, first: Arrow) -> SliceArrow:
        assert self.contains_slice_arrow(second)
        assert self.contains_slice_arrow(first)
        assert first.codomain() is second.domain()
        category = self.base_category()
        assert is_slice_over(category)
        return self(
            category.ambient_category().compose(
                second.varying_arrow(),
                first.varying_arrow(),
            )
        )

    def contains_slice_arrow(self, arrow: Arrow) -> TypeIs[SliceArrow]:
        return arrow in self


class CosliceHomCategory(HomCategory):
    """Commuting triangles under one fixed object."""

    ElementType = SliceArrow

    def __call__(self, right: Arrow) -> SliceArrow:
        category = self.base_category()
        assert is_coslice_under(category)
        source = self.domain()
        target = self.codomain()
        assert category.contains_coslice_object(source)
        assert category.contains_coslice_object(target)
        assert right in category.ambient_category().Hom(
            source.codomain(),
            target.codomain(),
        )
        return self.ObjectType(hom_category=self, varying_arrow=right)

    def identity(self) -> SliceArrow:
        assert self.domain() is self.codomain()
        category = self.base_category()
        assert is_coslice_under(category)
        assert category.contains_coslice_object(self.domain())
        return self(category.ambient_category().identity(self.domain().codomain()))

    def compose(self, second: Arrow, first: Arrow) -> SliceArrow:
        assert self.contains_slice_arrow(second)
        assert self.contains_slice_arrow(first)
        assert first.codomain() is second.domain()
        category = self.base_category()
        assert is_coslice_under(category)
        return self(
            category.ambient_category().compose(
                second.varying_arrow(),
                first.varying_arrow(),
            )
        )

    def contains_slice_arrow(self, arrow: Arrow) -> TypeIs[SliceArrow]:
        return arrow in self


class SliceOverCategory(Category):
    """The slice category ``C / X``."""

    def __init__(self, ambient_category: Category, target: MathematicalObject) -> None:
        assert target in ambient_category
        self._ambient_category = ambient_category
        self._target = target
        self._inclusion: InclusionFunctor | None = None
        super().__init__(
            object_type=ambient_category.ArrowType,
            category=SliceOverCategories(),
        )

    def ambient_category(self) -> Category:
        return self._ambient_category

    def target_object(self) -> MathematicalObject:
        return self._target

    def __contains__(self, candidate: MembershipInput) -> bool:
        arrow_category = self._ambient_category.ArrowCategory()
        return arrow_category.contains_arrow(candidate) and (
            candidate.codomain() is self._target
        )

    def contains_slice_object(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[Arrow]:
        return candidate in self

    def _hom_category_type(self) -> type[HomCategory]:
        return SliceHomCategory

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(
                self,
                self._ambient_category.ArrowCategory(),
            )
        return (self._inclusion,)

    def __repr__(self) -> str:
        return f"{self._ambient_category}/{self._target}"


class CosliceUnderCategory(Category):
    """The coslice category ``X \\ C``."""

    def __init__(self, ambient_category: Category, source: MathematicalObject) -> None:
        assert source in ambient_category
        self._ambient_category = ambient_category
        self._source = source
        self._inclusion: InclusionFunctor | None = None
        super().__init__(
            object_type=ambient_category.ArrowType,
            category=CosliceUnderCategories(),
        )

    def ambient_category(self) -> Category:
        return self._ambient_category

    def source_object(self) -> MathematicalObject:
        return self._source

    def __contains__(self, candidate: MembershipInput) -> bool:
        arrow_category = self._ambient_category.ArrowCategory()
        return arrow_category.contains_arrow(candidate) and (
            candidate.domain() is self._source
        )

    def contains_coslice_object(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[Arrow]:
        return candidate in self

    def _hom_category_type(self) -> type[HomCategory]:
        return CosliceHomCategory

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(
                self,
                self._ambient_category.ArrowCategory(),
            )
        return (self._inclusion,)

    def __repr__(self) -> str:
        return f"{self._source}\\{self._ambient_category}"


class SubobjectCategory(Category):
    """Monomorphisms into one fixed object."""

    def __init__(self, ambient_category: Category, target: MathematicalObject) -> None:
        self._ambient_category = ambient_category
        self._target = target
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=ambient_category.MonoArrowType)

    def __contains__(self, candidate: MembershipInput) -> bool:
        return candidate in SliceOver(self._ambient_category, self._target) and (
            candidate in self._ambient_category.MonomorphismArrowCategory()
        )

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(
                self,
                self._ambient_category.SliceOver(self._target),
            )
        return (self._inclusion,)


class SuperobjectCategory(Category):
    """Monomorphisms from one fixed object."""

    def __init__(self, ambient_category: Category, source: MathematicalObject) -> None:
        self._ambient_category = ambient_category
        self._source = source
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=ambient_category.MonoArrowType)

    def __contains__(self, candidate: MembershipInput) -> bool:
        return candidate in CosliceUnder(self._ambient_category, self._source) and (
            candidate in self._ambient_category.MonomorphismArrowCategory()
        )

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(
                self,
                self._ambient_category.CosliceUnder(self._source),
            )
        return (self._inclusion,)


class CoveringObjectCategory(Category):
    """Epimorphisms into one fixed object."""

    def __init__(self, ambient_category: Category, target: MathematicalObject) -> None:
        self._ambient_category = ambient_category
        self._target = target
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=ambient_category.EpiArrowType)

    def __contains__(self, candidate: MembershipInput) -> bool:
        return candidate in SliceOver(self._ambient_category, self._target) and (
            candidate in self._ambient_category.EpimorphismArrowCategory()
        )

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(
                self,
                self._ambient_category.SliceOver(self._target),
            )
        return (self._inclusion,)


class CoveredObjectCategory(Category):
    """Epimorphisms from one fixed object."""

    def __init__(self, ambient_category: Category, source: MathematicalObject) -> None:
        self._ambient_category = ambient_category
        self._source = source
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=ambient_category.EpiArrowType)

    def __contains__(self, candidate: MembershipInput) -> bool:
        return candidate in CosliceUnder(self._ambient_category, self._source) and (
            candidate in self._ambient_category.EpimorphismArrowCategory()
        )

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(
                self,
                self._ambient_category.CosliceUnder(self._source),
            )
        return (self._inclusion,)


class SliceOverCategoryObjects(Category):
    def __init__(self) -> None:
        super().__init__(object_type=SliceOverCategory)


class CosliceUnderCategoryObjects(Category):
    def __init__(self) -> None:
        super().__init__(object_type=CosliceUnderCategory)


_SLICE_OVER_CATEGORIES = SliceOverCategoryObjects()
_COSLICE_UNDER_CATEGORIES = CosliceUnderCategoryObjects()


def SliceOverCategories() -> SliceOverCategoryObjects:
    return _SLICE_OVER_CATEGORIES


def CosliceUnderCategories() -> CosliceUnderCategoryObjects:
    return _COSLICE_UNDER_CATEGORIES


def is_slice_over(category: Category) -> TypeIs[SliceOverCategory]:
    return category in SliceOverCategories()


def is_coslice_under(category: Category) -> TypeIs[CosliceUnderCategory]:
    return category in CosliceUnderCategories()


def SliceOver(
    ambient_category: Category,
    target: MathematicalObject,
) -> SliceOverCategory:
    return SliceOverCategory(ambient_category, target)


def CosliceUnder(
    ambient_category: Category,
    source: MathematicalObject,
) -> CosliceUnderCategory:
    return CosliceUnderCategory(ambient_category, source)


def Subobjects(
    ambient_category: Category,
    target: MathematicalObject,
) -> SubobjectCategory:
    return SubobjectCategory(ambient_category, target)


def Superobjects(
    ambient_category: Category,
    source: MathematicalObject,
) -> SuperobjectCategory:
    return SuperobjectCategory(ambient_category, source)


def CoveringObjects(
    ambient_category: Category,
    target: MathematicalObject,
) -> CoveringObjectCategory:
    return CoveringObjectCategory(ambient_category, target)


def CoveredObjects(
    ambient_category: Category,
    source: MathematicalObject,
) -> CoveredObjectCategory:
    return CoveredObjectCategory(ambient_category, source)


def Slice(structure_morphism: Arrow) -> Arrow:
    """Place an arrow as an object of its slice category."""
    category = structure_morphism.base_category()
    assert structure_morphism in category.SliceOver(structure_morphism.codomain())
    return structure_morphism


def Coslice(costructure_morphism: Arrow) -> Arrow:
    """Place an arrow as an object of its coslice category."""
    category = costructure_morphism.base_category()
    assert costructure_morphism in category.CosliceUnder(
        costructure_morphism.domain()
    )
    return costructure_morphism


def Subobject(structure_morphism: Arrow) -> Arrow:
    """Construct a subobject from a declared monomorphism."""
    category = structure_morphism.base_category()
    if structure_morphism not in category.MonomorphismArrowCategory():
        structure_morphism = category.Mono(
            structure_morphism.domain(),
            structure_morphism.codomain(),
        )(structure_morphism)
    assert structure_morphism in category.Subobjects(structure_morphism.codomain())
    return structure_morphism


def Superobject(costructure_morphism: Arrow) -> Arrow:
    """Construct a superobject from a declared monomorphism."""
    category = costructure_morphism.base_category()
    if costructure_morphism not in category.MonomorphismArrowCategory():
        costructure_morphism = category.Mono(
            costructure_morphism.domain(),
            costructure_morphism.codomain(),
        )(costructure_morphism)
    assert costructure_morphism in category.Superobjects(
        costructure_morphism.domain()
    )
    return costructure_morphism


def Covering(structure_morphism: Arrow) -> Arrow:
    """Construct a covering object from a declared epimorphism."""
    category = structure_morphism.base_category()
    if structure_morphism not in category.EpimorphismArrowCategory():
        structure_morphism = category.Epi(
            structure_morphism.domain(),
            structure_morphism.codomain(),
        )(structure_morphism)
    assert structure_morphism in category.CoveringObjects(
        structure_morphism.codomain()
    )
    return structure_morphism


def Covered(costructure_morphism: Arrow) -> Arrow:
    """Construct a covered object from a declared epimorphism."""
    category = costructure_morphism.base_category()
    if costructure_morphism not in category.EpimorphismArrowCategory():
        costructure_morphism = category.Epi(
            costructure_morphism.domain(),
            costructure_morphism.codomain(),
        )(costructure_morphism)
    assert costructure_morphism in category.CoveredObjects(
        costructure_morphism.domain()
    )
    return costructure_morphism
