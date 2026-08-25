"""Owned runtime values for the categorical kernel."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import Functor
    from sage_categories.abstract_categories.hom_categories import HomCategory
    from sage_categories.category import Category


class Unknown(Enum):
    """The result of a mathematical question with no represented answer."""

    VALUE = "Unknown"

    def __bool__(self) -> bool:
        assert False, "Unknown is not a Boolean value"

    def __repr__(self) -> str:
        return "Unknown"


UNKNOWN = Unknown.VALUE
type Decision = bool | Unknown


class ImplementationRole(Enum):
    """One category-owned implementation role of a mathematical value."""

    OBJECT = "object"
    ELEMENT = "element"
    ARROW = "arrow"


_VALUES: dict[int, MathematicalObject] = {}
_ELEMENTS: dict[int, MathematicalElement] = {}


def registered_value[Candidate](candidate: Candidate) -> MathematicalObject | None:
    """Return the owned mathematical value represented by ``candidate``."""
    candidate_id = id(candidate)
    value = _VALUES.get(candidate_id)
    if value is not None and id(value) == candidate_id:
        return value
    return None


def registered_element[Candidate](candidate: Candidate) -> MathematicalElement | None:
    """Return the owned mathematical element represented by ``candidate``."""
    candidate_id = id(candidate)
    element = _ELEMENTS.get(candidate_id)
    if element is not None and id(element) == candidate_id:
        return element
    return None


class MathematicalObject:
    """An object of one owned category."""

    def __init__(self, *, category: Category | None) -> None:
        self._category = category
        self._object_structural_images: dict[
            tuple[int, int, int], MathematicalObject
        ] = {}
        self._element_structural_images: dict[
            tuple[int, int, int], MathematicalElement
        ] = {}
        self._morphism_structural_images: dict[
            tuple[int, int, int], Arrow
        ] = {}
        if category is not None:
            self._object_structural_images[
                (id(self), id(self), id(category))
            ] = self
        _VALUES[id(self)] = self

    def category(self) -> Category:
        """Return the category in which this object was constructed."""
        assert self._category is not None
        return self._category

    def Hom(self, target: MathematicalObject) -> HomCategory:
        """Return the hom category from this object to ``target``."""
        from sage_categories.abstract_categories.arrow_categories import common_category

        return common_category((self, target)).Hom(self, target)

    def End(self) -> HomCategory:
        """Return the endomorphism category of this object."""
        return self.category().End(self)

    def Aut(self) -> HomCategory:
        """Return the automorphism category of this object."""
        return self.category().Aut(self)

    def Iso(self, target: MathematicalObject) -> HomCategory:
        """Return the isomorphisms from this object to ``target``."""
        from sage_categories.abstract_categories.arrow_categories import common_category

        return common_category((self, target)).Iso(self, target)

    def Mono(self, target: MathematicalObject) -> HomCategory:
        """Return the monomorphisms from this object to ``target``."""
        from sage_categories.abstract_categories.arrow_categories import common_category

        return common_category((self, target)).Mono(self, target)

    def Epi(self, target: MathematicalObject) -> HomCategory:
        """Return the epimorphisms from this object to ``target``."""
        from sage_categories.abstract_categories.arrow_categories import common_category

        return common_category((self, target)).Epi(self, target)

    def identity(self) -> Arrow:
        """Return the identity arrow of this object."""
        return self.category().identity(self)

    def subobjects(self) -> Category:
        """Return the category of monomorphisms into this object."""
        return self.category().Subobjects(self)

    def superobjects(self) -> Category:
        """Return the category of monomorphisms from this object."""
        return self.category().Superobjects(self)

    def covering_objects(self) -> Category:
        """Return the category of epimorphisms into this object."""
        return self.category().CoveringObjects(self)

    def covered_objects(self) -> Category:
        """Return the category of epimorphisms from this object."""
        return self.category().CoveredObjects(self)

    def _belongs_to(self, category: Category) -> bool:
        if self._category is None:
            return False
        return self._category is category or self._category.is_subcategory(category)

    def _belongs_to_hom(self, hom_category: HomCategory) -> bool:
        return False

    def _is_arrow_in(self, category: Category) -> bool:
        return False

    def _ambient_implementation(self) -> MathematicalObject:
        """Return the canonical implementation used by forgetting or inclusion."""
        return self

    def _defining_component(self, index: int) -> MathematicalObject:
        """Return component ``index`` of the standard defining-data tuple."""
        defining_data = self._defining_data
        assert isinstance(defining_data, tuple)
        assert 0 <= index < len(defining_data)
        component = registered_value(defining_data[index])
        assert component is not None, (
            f"component {index} of {self} is not an owned mathematical value"
        )
        return component

    def _implementation_contexts(
        self,
    ) -> tuple[tuple[ImplementationRole, Category], ...]:
        """Return the exact category-owned roles this value inhabits."""
        return ((ImplementationRole.OBJECT, self.category()),)

    def _implementation_image(
        self,
        role: ImplementationRole,
        route: tuple[Functor, ...],
    ) -> MathematicalObject:
        """Return this receiver's image in one exact implementation role."""
        assert role is ImplementationRole.OBJECT
        return self._object_image_along(route)

    def _implementation_ambient(
        self,
        role: ImplementationRole,
    ) -> MathematicalObject:
        """Return the ambient object used to reverse-transport role results."""
        assert role is ImplementationRole.OBJECT
        return self

    def _object_image_along(
        self,
        route: tuple[Functor, ...],
    ) -> MathematicalObject:
        """Return the canonical object image along one selected route."""
        from sage_categories.compiler import category_compiler

        if route:
            route = category_compiler().implementation_route(
                route[0].domain(),
                route[-1].codomain(),
            )
        value = self
        for functor in route:
            source = value
            key = id(source), id(value), id(functor.codomain())
            cached = self._object_structural_images.get(key)
            if cached is not None:
                value = cached
                continue
            value = functor.on_object(source)
            assert value in functor.codomain()
            self._object_structural_images[key] = value
        return value

    def _element_image_along(
        self,
        route: tuple[Functor, ...],
    ) -> MathematicalElement:
        assert False, f"{self} is not represented as an element"

    def _morphism_image_along(
        self,
        route: tuple[Functor, ...],
    ) -> Arrow:
        assert False, f"{self} is not represented as a morphism"


class TransportedObject(MathematicalObject):
    """An object constructed from one canonical ambient image."""

    def __init__(
        self,
        *,
        category: Category,
        ambient_implementation: MathematicalObject,
    ) -> None:
        self._ambient_implementation_value = ambient_implementation
        super().__init__(category=category)

    def _ambient_implementation(self) -> MathematicalObject:
        return self._ambient_implementation_value


class MathematicalElement(MathematicalObject):
    """An element of a mathematical object."""

    def __init__(
        self,
        *,
        category: Category,
        ambient_object: MathematicalObject,
    ) -> None:
        self._ambient_object = ambient_object
        super().__init__(category=category)
        _ELEMENTS[id(self)] = self
        self._element_structural_images[
            (id(ambient_object), id(self), id(ambient_object.category()))
        ] = self

    def ambient_object(self) -> MathematicalObject:
        """Return the mathematical object which contains this element."""
        return self._ambient_object

    def _ambient_implementation(self) -> MathematicalElement:
        """Return the canonical ambient element used by forgetting or inclusion."""
        return self

    def _defining_component(self, index: int) -> MathematicalElement:
        component = super()._defining_component(index)
        assert isinstance(component, MathematicalElement)
        return component

    def _implementation_contexts(
        self,
    ) -> tuple[tuple[ImplementationRole, Category], ...]:
        return (
            (ImplementationRole.ELEMENT, self.ambient_object().category()),
            *super()._implementation_contexts(),
        )

    def _implementation_image(
        self,
        role: ImplementationRole,
        route: tuple[Functor, ...],
    ) -> MathematicalObject:
        if role is ImplementationRole.ELEMENT:
            return self._element_image_along(route)
        return super()._implementation_image(role, route)

    def _implementation_ambient(
        self,
        role: ImplementationRole,
    ) -> MathematicalObject:
        if role is ImplementationRole.ELEMENT:
            return self.ambient_object()
        return super()._implementation_ambient(role)

    def _element_image_along(
        self,
        route: tuple[Functor, ...],
    ) -> MathematicalElement:
        """Return the canonical element image along one selected route."""
        from sage_categories.compiler import category_compiler

        if route:
            route = category_compiler().implementation_route(
                route[0].domain(),
                route[-1].codomain(),
            )
        ambient = self._ambient_object
        source = ambient
        element = self
        prefix: tuple[Functor, ...] = ()
        for functor in route:
            assert functor.maps_elements(), (
                f"selected functor {functor} cannot transport elements"
            )
            prefix = (*prefix, functor)
            key = id(source), id(element), id(functor.codomain())
            target = ambient._object_image_along(prefix)
            cached = self._element_structural_images.get(key)
            if cached is not None:
                assert cached.ambient_object() is target
                source = target
                element = cached
                continue
            element = functor.on_element(source, element)
            assert element.ambient_object() is target
            self._element_structural_images[key] = element
            source = target
        return element


class TransportedElement(MathematicalElement):
    """An element constructed from one canonical ambient element."""

    def __init__(
        self,
        *,
        category: Category,
        ambient_object: MathematicalObject,
        ambient_implementation: MathematicalElement,
    ) -> None:
        self._ambient_implementation_value = ambient_implementation
        super().__init__(category=category, ambient_object=ambient_object)

    def _ambient_implementation(self) -> MathematicalElement:
        return self._ambient_implementation_value

    @classmethod
    def _transported_from_ambient(
        cls,
        *,
        category: Category,
        ambient_object: MathematicalObject,
        ambient_implementation: MathematicalElement,
    ) -> Self:
        return cls(
            category=category,
            ambient_object=ambient_object,
            ambient_implementation=ambient_implementation,
        )


class CategoryElement(MathematicalElement):
    """The local element type when a category adds no element operations."""


class Arrow(MathematicalElement):
    """An object of ``Ar(C)`` and an element of one hom category of ``C``."""

    def __init__(self, *, hom_category: HomCategory) -> None:
        self._hom_category = hom_category
        MathematicalElement.__init__(
            self,
            category=hom_category.base_category().ArrowCategory(),
            ambient_object=hom_category,
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

    def _ambient_implementation(self) -> Arrow:
        """Return the canonical ambient arrow used by forgetting or inclusion."""
        return self

    def _defining_component(self, index: int) -> Arrow:
        component = super()._defining_component(index)
        assert isinstance(component, Arrow)
        return component

    def _implementation_contexts(
        self,
    ) -> tuple[tuple[ImplementationRole, Category], ...]:
        return (
            (ImplementationRole.ARROW, self.base_category()),
            *super()._implementation_contexts(),
        )

    def _implementation_image(
        self,
        role: ImplementationRole,
        route: tuple[Functor, ...],
    ) -> MathematicalObject:
        if role is ImplementationRole.ARROW:
            return self._morphism_image_along(route)
        return super()._implementation_image(role, route)

    def _implementation_ambient(
        self,
        role: ImplementationRole,
    ) -> MathematicalObject:
        if role is ImplementationRole.ARROW:
            return self.codomain()
        return super()._implementation_ambient(role)

    def _belongs_to_hom(self, hom_category: HomCategory) -> bool:
        own_hom_category = self._hom_category
        return own_hom_category is hom_category or (
            own_hom_category.domain() is hom_category.domain()
            and own_hom_category.codomain() is hom_category.codomain()
            and own_hom_category.hom_category().is_subcategory(
                hom_category.hom_category()
            )
        )

    def _is_arrow_in(self, category: Category) -> bool:
        base = self.base_category()
        return base is category or base.is_subcategory(category)

    def _morphism_image_along(
        self,
        route: tuple[Functor, ...],
    ) -> Arrow:
        """Return the canonical arrow image along one selected route."""
        from sage_categories.compiler import category_compiler

        if route:
            route = category_compiler().implementation_route(
                route[0].domain(),
                route[-1].codomain(),
            )
        value = self
        prefix: tuple[Functor, ...] = ()
        for functor in route:
            prefix = (*prefix, functor)
            key = id(value.hom_category()), id(value), id(functor.codomain())
            domain = self.domain()._object_image_along(prefix)
            codomain = self.codomain()._object_image_along(prefix)
            cached = self._morphism_structural_images.get(key)
            if cached is not None:
                assert cached.domain() is domain
                assert cached.codomain() is codomain
                value = cached
                continue
            image = functor.on_morphism(value)
            assert functor.codomain().contains_arrow(image)
            assert image.domain() is domain
            assert image.codomain() is codomain
            self._morphism_structural_images[key] = image
            value = image
        return value

    def __mul__(self, first: Arrow) -> Arrow:
        """Return this arrow after ``first``."""
        return self.base_category().compose(self, first)


class TransportedArrow(Arrow):
    """An arrow constructed from one canonical ambient arrow."""

    def __init__(
        self,
        *,
        hom_category: HomCategory,
        ambient_implementation: Arrow,
    ) -> None:
        self._ambient_implementation_value = ambient_implementation
        super().__init__(hom_category=hom_category)

    def _ambient_implementation(self) -> Arrow:
        return self._ambient_implementation_value

    @classmethod
    def _transported_from_ambient(
        cls,
        *,
        hom_category: HomCategory,
        ambient_implementation: Arrow,
    ) -> Self:
        return cls(
            hom_category=hom_category,
            ambient_implementation=ambient_implementation,
        )
