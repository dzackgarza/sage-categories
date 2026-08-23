"""Hom, endomorphism, monomorphism, epimorphism, and isomorphism categories.

The semantics are migrated from the research preamble's
``abstract_categories/hom_categories.sage``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.category import Category
from sage_categories.values import (
    Arrow,
    MathematicalObject,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import StructuralFunctor


class HomCategory(Category):
    """One category ``Hom_C(X, Y)`` whose objects are arrows of ``C``."""

    ObjectType: type[Arrow] = Arrow
    ElementType: type[Arrow] = Arrow

    def __init__(
        self,
        *,
        domain: MathematicalObject,
        codomain: MathematicalObject,
        hom_category: HomCategoryFamily,
    ) -> None:
        self._domain = domain
        self._codomain = codomain
        self._hom_category = hom_category
        arrow_type = hom_category.ElementType
        super().__init__(
            object_type=arrow_type,
            element_type=arrow_type,
            category=hom_category,
        )

    def domain(self) -> MathematicalObject:
        """Return the source shared by this hom category."""
        return self._domain

    def codomain(self) -> MathematicalObject:
        """Return the target shared by this hom category."""
        return self._codomain

    def hom_category(self) -> HomCategoryFamily:
        """Return the family containing this hom category."""
        return self._hom_category

    def base_category(self) -> Category:
        """Return the category whose arrows these are."""
        return self._hom_category.base_category()

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and value._belongs_to_hom(self)

    def include(self, arrow: Arrow) -> Arrow:
        """Return an arrow already contained in this hom category."""
        assert arrow in self
        return arrow

    def identity(self, value: MathematicalObject | None = None) -> Arrow:
        """Construct the identity when this is an endomorphism category."""
        if value is not None:
            return Category.identity(self, value)
        assert False, f"{self.base_category()} does not define identity arrows"

    def compose(self, second: Arrow, first: Arrow) -> Arrow:
        """Construct ``second`` after ``first``."""
        assert False, f"{self.base_category()} does not define arrow composition"

    def __repr__(self) -> str:
        return f"Hom({self._domain}, {self._codomain}) in {self.base_category()}"


class HomCategoryFamily(Category):
    """The category whose objects are the hom categories of one category."""

    ObjectType: type[HomCategory] = HomCategory
    ElementType: type[Arrow] = Arrow

    def __init__(
        self,
        base_category: Category,
        *,
        hom_category_type: type[HomCategory] = HomCategory,
    ) -> None:
        self._base_category = base_category
        self._member_type = hom_category_type
        self._hom_categories: dict[tuple[int, int], HomCategory] = {}
        super().__init__(
            object_type=hom_category_type,
            element_type=hom_category_type.ElementType,
        )

    def base_category(self) -> Category:
        """Return the category whose hom categories form this family."""
        return self._base_category

    def Of(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> HomCategory:
        """Return ``Hom_C(domain, codomain)``."""
        assert domain in self._base_category
        assert codomain in self._base_category
        key = id(domain), id(codomain)
        cached = self._hom_categories.get(key)
        if cached is not None:
            return cached
        result = self.ObjectType(
            domain=domain,
            codomain=codomain,
            hom_category=self,
        )
        self._hom_categories[key] = result
        return result

    def Between(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> HomCategory:
        """Return ``Hom_C(domain, codomain)``."""
        return self.Of(domain, codomain)

    def contains_hom_category(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[HomCategory]:
        """Return whether ``candidate`` is one hom category in this family."""
        return candidate in self

    def __repr__(self) -> str:
        return f"Hom categories of {self._base_category}"


class RestrictedArrow(Arrow):
    """An arrow together with membership in a restricted arrow category."""

    def __init__(self, *, hom_category: HomCategory, underlying_arrow: Arrow) -> None:
        assert underlying_arrow in hom_category.base_category().Hom(
            hom_category.domain(),
            hom_category.codomain(),
        )
        self._underlying_arrow = underlying_arrow
        super().__init__(hom_category=hom_category)

    def underlying_arrow(self) -> Arrow:
        """Return the arrow in the unrestricted hom category."""
        return self._underlying_arrow

    def forward(self) -> Arrow:
        """Return the represented forward arrow."""
        return self._underlying_arrow


class Endomorphism(RestrictedArrow):
    """An arrow with equal source and target."""

    def is_endomorphism(self) -> bool:
        return True


class Monomorphism(RestrictedArrow):
    """An arrow declared monic."""

    def is_monomorphism(self) -> bool:
        return True


class Epimorphism(RestrictedArrow):
    """An arrow declared epic."""

    def is_epimorphism(self) -> bool:
        return True


class Isomorphism(Arrow):
    """Mutually inverse arrows represented as one isomorphism."""

    def __init__(
        self,
        *,
        hom_category: HomCategory,
        forward: Arrow,
        backward: Arrow,
    ) -> None:
        assert forward in hom_category.base_category().Hom(
            hom_category.domain(),
            hom_category.codomain(),
        )
        assert backward in hom_category.base_category().Hom(
            hom_category.codomain(),
            hom_category.domain(),
        )
        self._forward = forward
        self._backward = backward
        super().__init__(hom_category=hom_category)

    def forward(self) -> Arrow:
        """Return the forward arrow."""
        return self._forward

    def inverse(self) -> Isomorphism:
        """Return the inverse isomorphism."""
        from sage_categories.abstract_categories.arrow_categories import (
            declare_isomorphism,
        )

        inverse = declare_isomorphism(
            self._backward,
            self._forward,
        )
        assert is_isomorphism(inverse)
        return inverse

    def is_isomorphism(self) -> bool:
        return True

    def is_monomorphism(self) -> bool:
        return True

    def is_epimorphism(self) -> bool:
        return True

    def is_endomorphism(self) -> bool:
        return self.domain() is self.codomain()


class Automorphism(Isomorphism):
    """An isomorphism with equal source and target."""

    def is_automorphism(self) -> bool:
        return True

    def is_endomorphism(self) -> bool:
        return True


class RestrictedHomCategory(HomCategory):
    """A hom category whose arrows carry a declared restriction."""

    ObjectType: type[RestrictedArrow] = RestrictedArrow
    ElementType: type[RestrictedArrow] = RestrictedArrow

    def __call__(self, underlying_arrow: Arrow) -> RestrictedArrow:
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )

    def identity(self, value: MathematicalObject | None = None) -> RestrictedArrow:
        assert value is None
        assert self.domain() is self.codomain()
        return self(self.base_category().Hom(self.domain(), self.codomain()).identity())

    def compose(self, second: Arrow, first: Arrow) -> RestrictedArrow:
        assert first.codomain() is second.domain()
        return self(self.base_category().compose(second.forward(), first.forward()))


class EndomorphismHomCategory(RestrictedHomCategory):
    """One endomorphism category."""

    ObjectType = Endomorphism
    ElementType = Endomorphism


class MonomorphismHomCategory(RestrictedHomCategory):
    """One monomorphism category."""

    ObjectType = Monomorphism
    ElementType = Monomorphism


class EpimorphismHomCategory(RestrictedHomCategory):
    """One epimorphism category."""

    ObjectType = Epimorphism
    ElementType = Epimorphism


class IsomorphismHomCategory(HomCategory):
    """One category of isomorphisms between two objects."""

    ObjectType = Isomorphism
    ElementType = Isomorphism

    def __call__(self, forward: Arrow, backward: Arrow) -> Isomorphism:
        return self.ObjectType(
            hom_category=self,
            forward=forward,
            backward=backward,
        )

    def identity(self, value: MathematicalObject | None = None) -> Isomorphism:
        assert value is None
        assert self.domain() is self.codomain()
        identity = self.base_category().Hom(self.domain(), self.codomain()).identity()
        return self(identity, identity)

    def compose(self, second: Arrow, first: Arrow) -> Isomorphism:
        assert self.contains_isomorphism(second)
        assert self.contains_isomorphism(first)
        assert first.codomain() is second.domain()
        category = self.base_category()
        return self(
            category.compose(second.forward(), first.forward()),
            category.compose(
                first.inverse().forward(),
                second.inverse().forward(),
            ),
        )

    def contains_isomorphism(self, arrow: Arrow) -> TypeIs[Isomorphism]:
        """Return whether ``arrow`` is an object of this isomorphism category."""
        return arrow in self


class AutomorphismHomCategory(IsomorphismHomCategory):
    """One automorphism category."""

    ObjectType = Automorphism
    ElementType = Automorphism


class EndCategoryFamily(HomCategoryFamily):
    """The endomorphism categories of one category."""

    def __init__(self, base_category: Category) -> None:
        self._inclusion: StructuralFunctor | None = None
        super().__init__(base_category, hom_category_type=EndomorphismHomCategory)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        from sage_categories.abstract_categories.functors import (
            HomCategoryFamilyInclusionFunctor,
        )

        if self._inclusion is None:
            self._inclusion = HomCategoryFamilyInclusionFunctor(
                self,
                self.base_category().HomCategory(),
            )
        return (self._inclusion,)

    def Of(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> HomCategory:
        assert domain is codomain
        return super().Of(domain, codomain)


class MonomorphismCategoryFamily(HomCategoryFamily):
    """The monomorphism categories of one category."""

    def __init__(self, base_category: Category) -> None:
        self._inclusion: StructuralFunctor | None = None
        super().__init__(base_category, hom_category_type=MonomorphismHomCategory)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        from sage_categories.abstract_categories.functors import (
            HomCategoryFamilyInclusionFunctor,
        )

        if self._inclusion is None:
            self._inclusion = HomCategoryFamilyInclusionFunctor(
                self,
                self.base_category().HomCategory(),
            )
        return (self._inclusion,)


class EpimorphismCategoryFamily(HomCategoryFamily):
    """The epimorphism categories of one category."""

    def __init__(self, base_category: Category) -> None:
        self._inclusion: StructuralFunctor | None = None
        super().__init__(base_category, hom_category_type=EpimorphismHomCategory)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        from sage_categories.abstract_categories.functors import (
            HomCategoryFamilyInclusionFunctor,
        )

        if self._inclusion is None:
            self._inclusion = HomCategoryFamilyInclusionFunctor(
                self,
                self.base_category().HomCategory(),
            )
        return (self._inclusion,)


class IsomorphismCategoryFamily(HomCategoryFamily):
    """The isomorphism categories of one category."""

    def __init__(self, base_category: Category) -> None:
        self._inclusion: StructuralFunctor | None = None
        super().__init__(base_category, hom_category_type=IsomorphismHomCategory)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        from sage_categories.abstract_categories.functors import (
            HomCategoryFamilyInclusionFunctor,
        )

        if self._inclusion is None:
            self._inclusion = HomCategoryFamilyInclusionFunctor(
                self,
                self.base_category().MonoCategory(),
            )
        return (self._inclusion,)

    def is_subcategory(self, category: Category) -> bool:
        return category is self.base_category().EpiCategory() or super().is_subcategory(category)


class AutomorphismCategoryFamily(HomCategoryFamily):
    """The automorphism categories of one category."""

    def __init__(self, base_category: Category) -> None:
        self._inclusion: StructuralFunctor | None = None
        super().__init__(base_category, hom_category_type=AutomorphismHomCategory)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        from sage_categories.abstract_categories.functors import (
            HomCategoryFamilyInclusionFunctor,
        )

        if self._inclusion is None:
            self._inclusion = HomCategoryFamilyInclusionFunctor(
                self,
                self.base_category().IsoCategory(),
            )
        return (self._inclusion,)

    def is_subcategory(self, category: Category) -> bool:
        return category is self.base_category().EndCategory() or super().is_subcategory(category)

    def Of(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> HomCategory:
        assert domain is codomain
        return super().Of(domain, codomain)


def is_isomorphism_hom_category(
    category: HomCategory,
) -> TypeIs[IsomorphismHomCategory]:
    """Return whether ``category`` belongs to an isomorphism family."""
    base = category.base_category()
    return category in base.IsoCategory() or category in base.AutCategory()


def is_isomorphism(arrow: Arrow) -> TypeIs[Isomorphism]:
    """Return whether ``arrow`` is in an isomorphism arrow category."""
    category = arrow.base_category()
    return arrow in category.IsomorphismArrowCategory() or arrow in category.AutomorphismArrowCategory()


def is_restricted_hom_category(
    category: HomCategory,
) -> TypeIs[RestrictedHomCategory]:
    """Return whether ``category`` constructs restricted arrows."""
    base = category.base_category()
    return category in base.EndCategory() or category in base.MonoCategory() or category in base.EpiCategory()
