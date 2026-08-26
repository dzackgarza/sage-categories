"""Hom, endomorphism, monomorphism, epimorphism, and isomorphism categories.

The semantics are migrated from the research preamble's
``abstract_categories/hom_categories.sage``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.category import Category
from sage_categories.types import (
    Arrow,
    MathematicalObject,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import ConcreteFunctor, Functor


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

    def identity(self) -> Arrow:
        """Construct the identity when this is an endomorphism category."""
        assert self.domain() is self.codomain()
        target = self.domain()._ambient_implementation().category()
        route = self._declared_arrow_route(target)
        image_domain = self.domain()._object_image_along(route)
        image = route[-1].codomain().identity(image_domain)
        return self._lift_along_declared_route(image, route)

    def compose(self, second: Arrow, first: Arrow) -> Arrow:
        """Construct ``second`` after ``first``."""
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        target = first._ambient_implementation().base_category()
        route = self._declared_arrow_route(target)
        image = route[-1].codomain().compose(
            second._morphism_image_along(route),
            first._morphism_image_along(route),
        )
        return self._lift_along_declared_route(image, route)

    def _declared_arrow_route(
        self,
        target: Category,
    ) -> tuple[Functor, ...]:
        route = self.base_category().structural_route_to(target)
        assert route, f"{self.base_category()} declares no arrow construction route"
        assert all(
            functor in functor.hom_category().Faithful()
            for functor in route
        ), (
            f"the declared route from {self.base_category()} to {target} is not faithful"
        )
        return route

    def _lift_along_declared_route(
        self,
        image: Arrow,
        route: tuple[Functor, ...],
    ) -> Arrow:
        sources = [self.domain()]
        targets = [self.codomain()]
        for functor in route[:-1]:
            sources.append(functor.on_object(sources[-1]))
            targets.append(functor.on_object(targets[-1]))
        lifted = image
        for functor, source, target in reversed(
            tuple(zip(route, sources, targets, strict=True))
        ):
            lifted = functor._lift_morphism(source, target, lifted)
        return lifted

    def _from_structural_image(self, image: Arrow) -> Arrow:
        route = self._declared_arrow_route(image.base_category())
        assert image in route[-1].codomain().Hom(
            self.domain()._object_image_along(route),
            self.codomain()._object_image_along(route),
        )
        return self._lift_along_declared_route(image, route)

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
        self._inverse_isomorphism: Isomorphism | None = None
        super().__init__(hom_category=hom_category)
        _record_declared_isomorphism(self.domain(), self.codomain())

    def forward(self) -> Arrow:
        """Return the forward arrow."""
        return self._forward

    def inverse(self) -> Isomorphism:
        """Return the inverse isomorphism."""
        inverse = self._inverse_isomorphism
        if inverse is None:
            category = self.base_category()
            if self.domain() is self.codomain():
                inverse_hom = category.Aut(self.domain())
            else:
                inverse_hom = category.Iso(self.codomain(), self.domain())
            assert is_isomorphism_hom_category(inverse_hom)
            inverse = inverse_hom(self._backward, self._forward)
            inverse._inverse_isomorphism = self
            self._inverse_isomorphism = inverse
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


_DECLARED_ISOMORPHISM_CLASSES: dict[
    int,
    dict[int, MathematicalObject],
] = {}


def _record_declared_isomorphism(
    domain: MathematicalObject,
    codomain: MathematicalObject,
) -> None:
    component = {
        id(domain): domain,
        id(codomain): codomain,
    }
    domain_component = _DECLARED_ISOMORPHISM_CLASSES.get(id(domain))
    if domain_component is not None:
        component.update(domain_component)
    codomain_component = _DECLARED_ISOMORPHISM_CLASSES.get(id(codomain))
    if codomain_component is not None:
        component.update(codomain_component)
    for value in component.values():
        _DECLARED_ISOMORPHISM_CLASSES[id(value)] = component


def _declared_isomorphic_objects(
    value: MathematicalObject,
) -> tuple[MathematicalObject, ...]:
    component = _DECLARED_ISOMORPHISM_CLASSES.get(id(value))
    if component is None:
        return (value,)
    return tuple(component.values())


class RestrictedHomCategory(HomCategory):
    """A hom category whose arrows carry a declared restriction."""

    ObjectType: type[RestrictedArrow] = RestrictedArrow
    ElementType: type[RestrictedArrow] = RestrictedArrow

    def __call__(self, underlying_arrow: Arrow) -> RestrictedArrow:
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )

    def identity(self) -> RestrictedArrow:
        assert self.domain() is self.codomain()
        return self(self.base_category().Hom(self.domain(), self.codomain()).identity())

    def compose(self, second: Arrow, first: Arrow) -> RestrictedArrow:
        assert first.hom_category() in self.hom_category()
        assert second.hom_category() in self.hom_category()
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
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

    def __init__(
        self,
        *,
        domain: MathematicalObject,
        codomain: MathematicalObject,
        hom_category: HomCategoryFamily,
    ) -> None:
        self._isomorphisms: dict[tuple[int, int], Isomorphism] = {}
        super().__init__(
            domain=domain,
            codomain=codomain,
            hom_category=hom_category,
        )

    def __call__(self, forward: Arrow, backward: Arrow) -> Isomorphism:
        key = id(forward), id(backward)
        cached = self._isomorphisms.get(key)
        if cached is not None:
            return cached
        result = self.ObjectType(
            hom_category=self,
            forward=forward,
            backward=backward,
        )
        self._isomorphisms[key] = result
        return result

    def identity(self) -> Isomorphism:
        assert self.domain() is self.codomain()
        identity = self.base_category().Hom(self.domain(), self.codomain()).identity()
        return self(identity, identity)

    def compose(self, second: Arrow, first: Arrow) -> Isomorphism:
        assert is_isomorphism(second)
        assert is_isomorphism(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
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
        self._inclusion: ConcreteFunctor | None = None
        super().__init__(base_category, hom_category_type=EndomorphismHomCategory)

    def structure_functors(self) -> tuple[Functor, ...]:
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
        self._inclusion: ConcreteFunctor | None = None
        super().__init__(base_category, hom_category_type=MonomorphismHomCategory)

    def structure_functors(self) -> tuple[Functor, ...]:
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
        self._inclusion: ConcreteFunctor | None = None
        super().__init__(base_category, hom_category_type=EpimorphismHomCategory)

    def structure_functors(self) -> tuple[Functor, ...]:
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
        self._inclusion: ConcreteFunctor | None = None
        super().__init__(base_category, hom_category_type=IsomorphismHomCategory)

    def structure_functors(self) -> tuple[Functor, ...]:
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
        self._inclusion: ConcreteFunctor | None = None
        super().__init__(base_category, hom_category_type=AutomorphismHomCategory)

    def structure_functors(self) -> tuple[Functor, ...]:
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
