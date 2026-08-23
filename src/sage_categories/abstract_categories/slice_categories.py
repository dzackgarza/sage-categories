"""Slice, coslice, subobject, and covering-object categories."""

from __future__ import annotations

from typing import Any, TypeIs

from sage_categories.abstract_categories.category_constructions import (
    FullSubcategory,
)
from sage_categories.abstract_categories.functors import (
    StructuralFunctor,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    is_restricted_hom_category,
)
from sage_categories.category import Category
from sage_categories.values import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
    registered_value,
)


class SliceObject(MathematicalObject):
    """An object together with its defining arrow in a slice or coslice."""

    def __init__(
        self,
        *,
        category: Category,
        varying_object: MathematicalObject,
        fixed_object: MathematicalObject,
        structure_morphism: Arrow,
    ) -> None:
        self._varying_object = varying_object
        self._fixed_object = fixed_object
        self._structure_morphism = structure_morphism
        super().__init__(category=category)

    def object(self) -> MathematicalObject:
        return self._varying_object

    def fixed_object(self) -> MathematicalObject:
        return self._fixed_object

    def structure_morphism(self) -> Arrow:
        return self._structure_morphism


class SubobjectObject(SliceObject):
    """An object equipped with a monomorphism into one fixed object."""

    def intersection(self, other: MathematicalObject) -> SubobjectObject:
        ambient = self.structure_morphism().base_category()
        category = ambient.Subobjects(self.fixed_object())
        assert category.contains_subobject(self)
        assert category.contains_subobject(other)
        assert self.fixed_object() is other.fixed_object()
        return category.intersection(self, other)


class SliceForgetfulFunctor(StructuralFunctor):
    """Send a chosen arrow object to its varying ambient object."""

    def __init__(
        self,
        domain: SliceOverCategory | CosliceUnderCategory,
    ) -> None:
        self._slice_category = domain
        super().__init__(domain, domain.ambient_category())

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        assert self._slice_category.contains_slice_object(source)
        return source.object()

    def on_morphism(self, morphism: Arrow) -> Arrow:
        assert self._slice_category.contains_slice_arrow(morphism)
        return morphism.varying_arrow()

    def on_element(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element


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

    ObjectType = SliceArrow
    ElementType = SliceArrow

    def __call__(self, left: Arrow) -> SliceArrow:
        category = self.base_category()
        assert is_slice_over(category)
        source = self.domain()
        target = self.codomain()
        assert category.contains_slice_object(source)
        assert category.contains_slice_object(target)
        assert left in category.ambient_category().Hom(source.object(), target.object())
        return self.ObjectType(hom_category=self, varying_arrow=left)

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> SliceArrow:
        assert value is None
        assert self.domain() is self.codomain()
        category = self.base_category()
        assert is_slice_over(category)
        domain = self.domain()
        assert category.contains_slice_object(domain)
        return self(category.ambient_category().identity(domain.object()))

    def compose(self, second: Arrow, first: Arrow) -> SliceArrow:
        category = self.base_category()
        assert is_slice_over(category)
        assert category.contains_slice_arrow(second)
        assert category.contains_slice_arrow(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
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

    ObjectType = SliceArrow
    ElementType = SliceArrow

    def __call__(self, right: Arrow) -> SliceArrow:
        category = self.base_category()
        assert is_coslice_under(category)
        source = self.domain()
        target = self.codomain()
        assert category.contains_coslice_object(source)
        assert category.contains_coslice_object(target)
        assert right in category.ambient_category().Hom(source.object(), target.object())
        return self.ObjectType(hom_category=self, varying_arrow=right)

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> SliceArrow:
        assert value is None
        assert self.domain() is self.codomain()
        category = self.base_category()
        assert is_coslice_under(category)
        domain = self.domain()
        assert category.contains_coslice_object(domain)
        return self(category.ambient_category().identity(domain.object()))

    def compose(self, second: Arrow, first: Arrow) -> SliceArrow:
        category = self.base_category()
        assert is_coslice_under(category)
        assert category.contains_slice_arrow(second)
        assert category.contains_slice_arrow(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
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

    ObjectType: type[SliceObject] = SliceObject

    def __init__(self, ambient_category: Category, target: MathematicalObject) -> None:
        assert target in ambient_category
        self._ambient_category = ambient_category
        self._target = target
        self._forgetful: SliceForgetfulFunctor | None = None
        super().__init__(
            object_type=SliceObject,
            category=SliceOverCategories(),
        )

    def __call__(self, structure_morphism: Arrow) -> SliceObject:
        assert structure_morphism in self._ambient_category.ArrowCategory()
        assert structure_morphism.codomain() is self._target
        return self.ObjectType(
            category=self,
            varying_object=structure_morphism.domain(),
            fixed_object=self._target,
            structure_morphism=structure_morphism,
        )

    def ambient_category(self) -> Category:
        return self._ambient_category

    def target_object(self) -> MathematicalObject:
        return self._target

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and value._belongs_to(self)

    def contains_slice_object(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[SliceObject]:
        return candidate in self

    def contains_slice_arrow(self, candidate: Arrow) -> TypeIs[SliceArrow]:
        return candidate in self.ArrowCategory()

    def _hom_category_type(self) -> type[HomCategory]:
        return SliceHomCategory

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._forgetful is None:
            self._forgetful = SliceForgetfulFunctor(self)
        return (self._forgetful,)

    def __repr__(self) -> str:
        return f"{self._ambient_category}/{self._target}"


class CosliceUnderCategory(Category):
    """The coslice category ``X \\ C``."""

    ObjectType: type[SliceObject] = SliceObject

    def __init__(self, ambient_category: Category, source: MathematicalObject) -> None:
        assert source in ambient_category
        self._ambient_category = ambient_category
        self._source = source
        self._forgetful: SliceForgetfulFunctor | None = None
        super().__init__(
            object_type=SliceObject,
            category=CosliceUnderCategories(),
        )

    def __call__(self, structure_morphism: Arrow) -> SliceObject:
        assert structure_morphism in self._ambient_category.ArrowCategory()
        assert structure_morphism.domain() is self._source
        return self.ObjectType(
            category=self,
            varying_object=structure_morphism.codomain(),
            fixed_object=self._source,
            structure_morphism=structure_morphism,
        )

    def ambient_category(self) -> Category:
        return self._ambient_category

    def source_object(self) -> MathematicalObject:
        return self._source

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and value._belongs_to(self)

    def contains_coslice_object(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[SliceObject]:
        return candidate in self

    def contains_slice_object(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[SliceObject]:
        return candidate in self

    def contains_slice_arrow(self, candidate: Arrow) -> TypeIs[SliceArrow]:
        return candidate in self.ArrowCategory()

    def _hom_category_type(self) -> type[HomCategory]:
        return CosliceHomCategory

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._forgetful is None:
            self._forgetful = SliceForgetfulFunctor(self)
        return (self._forgetful,)

    def __repr__(self) -> str:
        return f"{self._source}\\{self._ambient_category}"


class SubobjectCategory(FullSubcategory):
    """Monomorphisms into one fixed object."""

    ObjectType: type[SubobjectObject] = SubobjectObject

    def __init__(self, ambient_category: Category, target: MathematicalObject) -> None:
        self._base_category = ambient_category
        self._target = target
        super().__init__(
            ambient_category.SliceOver(target),
            self._is_subobject,
            name=f"Subobjects of {target}",
            object_type=SubobjectObject,
        )

    def _is_subobject(self, candidate: MathematicalObject) -> bool:
        slice_category = self.ambient_category()
        assert is_slice_over(slice_category)
        assert slice_category.contains_slice_object(candidate)
        return candidate.structure_morphism() in self._base_category.MonomorphismArrowCategory()

    def __call__(self, structure_morphism: Arrow) -> SubobjectObject:
        assert structure_morphism in self._base_category.MonomorphismArrowCategory()
        assert structure_morphism.codomain() is self._target
        return self.ObjectType(
            category=self,
            varying_object=structure_morphism.domain(),
            fixed_object=self._target,
            structure_morphism=structure_morphism,
        )

    def intersection(
        self,
        first: MathematicalObject,
        second: MathematicalObject,
    ) -> SubobjectObject:
        assert self.contains_subobject(first)
        assert self.contains_subobject(second)
        pullback = self._base_category.pullback(
            first.structure_morphism(),
            second.structure_morphism(),
        )
        apex = pullback.image()
        projection = pullback.projection(first.object())
        structure_morphism = self._base_category.compose(
            first.structure_morphism(),
            projection,
        )
        monomorphisms = self._base_category.Mono(apex, self._target)
        assert is_restricted_hom_category(monomorphisms)
        return self(monomorphisms(structure_morphism))

    def contains_subobject(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[SliceObject]:
        return candidate in self


class SuperobjectCategory(FullSubcategory):
    """Monomorphisms from one fixed object."""

    ObjectType: type[SliceObject] = SliceObject

    def __init__(self, ambient_category: Category, source: MathematicalObject) -> None:
        self._base_category = ambient_category
        self._source = source
        super().__init__(
            ambient_category.CosliceUnder(source),
            self._is_superobject,
            name=f"Superobjects of {source}",
            object_type=SliceObject,
        )

    def _is_superobject(self, candidate: MathematicalObject) -> bool:
        coslice_category = self.ambient_category()
        assert is_coslice_under(coslice_category)
        assert coslice_category.contains_slice_object(candidate)
        return candidate.structure_morphism() in self._base_category.MonomorphismArrowCategory()

    def __call__(self, structure_morphism: Arrow) -> SliceObject:
        assert structure_morphism in self._base_category.MonomorphismArrowCategory()
        assert structure_morphism.domain() is self._source
        return self.ObjectType(
            category=self,
            varying_object=structure_morphism.codomain(),
            fixed_object=self._source,
            structure_morphism=structure_morphism,
        )


class CoveringObjectCategory(FullSubcategory):
    """Epimorphisms into one fixed object."""

    ObjectType: type[SliceObject] = SliceObject

    def __init__(self, ambient_category: Category, target: MathematicalObject) -> None:
        self._base_category = ambient_category
        self._target = target
        super().__init__(
            ambient_category.SliceOver(target),
            self._is_covering_object,
            name=f"Covering objects of {target}",
            object_type=SliceObject,
        )

    def _is_covering_object(self, candidate: MathematicalObject) -> bool:
        slice_category = self.ambient_category()
        assert is_slice_over(slice_category)
        assert slice_category.contains_slice_object(candidate)
        return candidate.structure_morphism() in self._base_category.EpimorphismArrowCategory()

    def __call__(self, structure_morphism: Arrow) -> SliceObject:
        assert structure_morphism in self._base_category.EpimorphismArrowCategory()
        assert structure_morphism.codomain() is self._target
        return self.ObjectType(
            category=self,
            varying_object=structure_morphism.domain(),
            fixed_object=self._target,
            structure_morphism=structure_morphism,
        )


class CoveredObjectCategory(FullSubcategory):
    """Epimorphisms from one fixed object."""

    ObjectType: type[SliceObject] = SliceObject

    def __init__(self, ambient_category: Category, source: MathematicalObject) -> None:
        self._base_category = ambient_category
        self._source = source
        super().__init__(
            ambient_category.CosliceUnder(source),
            self._is_covered_object,
            name=f"Covered objects of {source}",
            object_type=SliceObject,
        )

    def _is_covered_object(self, candidate: MathematicalObject) -> bool:
        coslice_category = self.ambient_category()
        assert is_coslice_under(coslice_category)
        assert coslice_category.contains_slice_object(candidate)
        return candidate.structure_morphism() in self._base_category.EpimorphismArrowCategory()

    def __call__(self, structure_morphism: Arrow) -> SliceObject:
        assert structure_morphism in self._base_category.EpimorphismArrowCategory()
        assert structure_morphism.domain() is self._source
        return self.ObjectType(
            category=self,
            varying_object=structure_morphism.codomain(),
            fixed_object=self._source,
            structure_morphism=structure_morphism,
        )


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


def Slice(structure_morphism: Arrow) -> SliceObject:
    """Construct the object represented by an arrow into a fixed object."""
    category = structure_morphism.base_category()
    slice_category = category.SliceOver(structure_morphism.codomain())
    assert is_slice_over(slice_category)
    return slice_category(structure_morphism)


def Coslice(costructure_morphism: Arrow) -> SliceObject:
    """Construct the object represented by an arrow from a fixed object."""
    category = costructure_morphism.base_category()
    coslice_category = category.CosliceUnder(costructure_morphism.domain())
    assert is_coslice_under(coslice_category)
    return coslice_category(costructure_morphism)


def Subobject(structure_morphism: Arrow) -> SliceObject:
    """Construct a subobject from a declared monomorphism."""
    category = structure_morphism.base_category()
    if structure_morphism not in category.MonomorphismArrowCategory():
        monomorphisms = category.Mono(
            structure_morphism.domain(),
            structure_morphism.codomain(),
        )
        assert is_restricted_hom_category(monomorphisms)
        structure_morphism = monomorphisms(structure_morphism)
    subobjects = category.Subobjects(structure_morphism.codomain())
    assert subobjects.is_subcategory(category.SliceOver(structure_morphism.codomain()))
    result = subobjects(structure_morphism)
    assert result in subobjects
    return result


def Superobject(costructure_morphism: Arrow) -> SliceObject:
    """Construct a superobject from a declared monomorphism."""
    category = costructure_morphism.base_category()
    if costructure_morphism not in category.MonomorphismArrowCategory():
        monomorphisms = category.Mono(
            costructure_morphism.domain(),
            costructure_morphism.codomain(),
        )
        assert is_restricted_hom_category(monomorphisms)
        costructure_morphism = monomorphisms(costructure_morphism)
    superobjects = category.Superobjects(costructure_morphism.domain())
    assert superobjects.is_subcategory(category.CosliceUnder(costructure_morphism.domain()))
    return superobjects(costructure_morphism)


def Covering(structure_morphism: Arrow) -> SliceObject:
    """Construct a covering object from a declared epimorphism."""
    category = structure_morphism.base_category()
    if structure_morphism not in category.EpimorphismArrowCategory():
        epimorphisms = category.Epi(
            structure_morphism.domain(),
            structure_morphism.codomain(),
        )
        assert is_restricted_hom_category(epimorphisms)
        structure_morphism = epimorphisms(structure_morphism)
    coverings = category.CoveringObjects(structure_morphism.codomain())
    assert coverings.is_subcategory(category.SliceOver(structure_morphism.codomain()))
    return coverings(structure_morphism)


def Covered(costructure_morphism: Arrow) -> SliceObject:
    """Construct a covered object from a declared epimorphism."""
    category = costructure_morphism.base_category()
    if costructure_morphism not in category.EpimorphismArrowCategory():
        epimorphisms = category.Epi(
            costructure_morphism.domain(),
            costructure_morphism.codomain(),
        )
        assert is_restricted_hom_category(epimorphisms)
        costructure_morphism = epimorphisms(costructure_morphism)
    covered_objects = category.CoveredObjects(costructure_morphism.domain())
    assert covered_objects.is_subcategory(category.CosliceUnder(costructure_morphism.domain()))
    return covered_objects(costructure_morphism)
