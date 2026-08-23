"""Diagram shapes."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.abstract_categories.functors import (
    ConstantDiagram,
    Functor,
    InclusionFunctor,
    NaturalTransformation,
    StructuralFunctor,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
)
from sage_categories.category import Category
from sage_categories.values import (
    Arrow,
    MathematicalObject,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.sets import FiniteSetObject, SetElement


class DiagramHomCategory(HomCategory):
    """The admitted arrows between two objects of a declared diagram."""

    def diagram_category(self) -> DiagramCategory:
        category = self.base_category()
        assert is_diagram_category(category)
        return category

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        if value is None:
            return False
        diagram = self.diagram_category()
        if not diagram.ambient_category().contains_arrow(value):
            return False
        forward = value.forward()
        return (
            value.domain() is self.domain()
            and value.codomain() is self.codomain()
            and forward
            in diagram.ambient_category().Hom(self.domain(), self.codomain())
            and diagram.contains_arrow(value)
        )

    def __call__(self, arrow: Arrow) -> Arrow:
        assert arrow in self
        return arrow

    def identity(self, value: MathematicalObject | None = None) -> Arrow:
        assert value is None
        assert self.domain() is self.codomain()
        diagram = self.diagram_category()
        identity = (
            diagram.ambient_category().Hom(self.domain(), self.domain()).identity()
        )
        diagram.admit(identity)
        return identity

    def compose(self, second: Arrow, first: Arrow) -> Arrow:
        assert first in self.diagram_category().ArrowCategory()
        assert second in self.diagram_category().ArrowCategory()
        assert first.codomain() is second.domain()
        diagram = self.diagram_category()
        composite = (
            diagram.ambient_category()
            .Hom(first.domain(), second.codomain())
            .compose(
                second.forward(),
                first.forward(),
            )
        )
        diagram.admit(composite)
        return composite


class DiagramCategory(Category):
    """A small declared diagram inside one ambient category."""

    def __init__(
        self,
        ambient_category: Category,
        objects: tuple[MathematicalObject, ...],
        morphisms: tuple[Arrow, ...] = (),
    ) -> None:
        self._ambient_category = ambient_category
        self._diagram_objects = tuple(objects)
        self._diagram_morphisms = tuple(morphisms)
        self._admitted_arrows = {id(morphism): morphism for morphism in morphisms}
        self._ambient_inclusion: InclusionFunctor | None = None
        assert all(value in ambient_category for value in self._diagram_objects)
        assert all(ambient_category.contains_arrow(morphism) for morphism in morphisms)
        assert all(
            self._has_object(morphism.domain())
            and self._has_object(morphism.codomain())
            for morphism in morphisms
        )
        super().__init__(
            object_type=ambient_category.ObjectType,
            element_type=ambient_category.ElementType,
        )
        _DIAGRAM_CATEGORIES[id(self)] = self

    def ambient_category(self) -> Category:
        return self._ambient_category

    def diagram_objects(self) -> tuple[MathematicalObject, ...]:
        return self._diagram_objects

    def diagram_morphisms(self) -> tuple[Arrow, ...]:
        return self._diagram_morphisms

    def objects(self) -> FiniteSetObject:
        from sage_categories.theories.sets import FiniteSet

        return FiniteSet(frozenset(self._diagram_objects))

    def object_element(self, value: MathematicalObject) -> SetElement:
        assert value in self
        return self.objects().element(value)

    def arrows(self) -> FiniteSetObject:
        from sage_categories.theories.sets import FiniteSet

        return FiniteSet(frozenset(self._diagram_morphisms))

    def _has_object(self, candidate: MathematicalObject) -> bool:
        return any(candidate is value for value in self._diagram_objects)

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and self._has_object(value)

    def contains_arrow(self, candidate: MathematicalObject) -> TypeIs[Arrow]:
        if not self._ambient_category.contains_arrow(candidate):
            return False
        admitted = self._admitted_arrows.get(id(candidate))
        if admitted is candidate:
            return True
        forward = candidate.forward()
        if forward is candidate:
            return False
        admitted_forward = self._admitted_arrows.get(id(forward))
        return admitted_forward is forward

    def admit(self, arrow: Arrow) -> Arrow:
        assert arrow in self._ambient_category.ArrowCategory()
        assert self._has_object(arrow.domain())
        assert self._has_object(arrow.codomain())
        self._admitted_arrows[id(arrow)] = arrow
        return arrow

    def _hom_category_type(self) -> type[HomCategory]:
        return DiagramHomCategory

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._ambient_inclusion is None:
            self._ambient_inclusion = InclusionFunctor(self, self._ambient_category)
        return (self._ambient_inclusion,)

    def __repr__(self) -> str:
        return f"Diagram({self._diagram_objects}) in {self._ambient_category}"


class DirectedSystem(DiagramCategory):
    """A directed system indexed by one ordered set."""

    def __init__(
        self,
        ambient_category: Category,
        index_set: MathematicalObject,
        objects: tuple[MathematicalObject, ...],
        morphisms: tuple[Arrow, ...] = (),
    ) -> None:
        self._index_set = index_set
        self._diagram_category = DiagramCategory(
            ambient_category,
            objects,
            morphisms,
        )
        self._diagram_inclusion: InclusionFunctor | None = None
        super().__init__(ambient_category, objects, morphisms)

    def index_set(self) -> MathematicalObject:
        return self._index_set

    def diagram_category(self) -> DiagramCategory:
        return self._diagram_category

    def admit(self, arrow: Arrow) -> Arrow:
        self._diagram_category.admit(arrow)
        return super().admit(arrow)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._diagram_inclusion is None:
            self._diagram_inclusion = InclusionFunctor(
                self,
                self._diagram_category,
            )
        return (self._diagram_inclusion,)


class InverseSystem(DiagramCategory):
    """An inverse system indexed by one ordered set."""

    def __init__(
        self,
        ambient_category: Category,
        index_set: MathematicalObject,
        objects: tuple[MathematicalObject, ...],
        morphisms: tuple[Arrow, ...] = (),
    ) -> None:
        self._index_set = index_set
        self._diagram_category = DiagramCategory(
            ambient_category,
            objects,
            morphisms,
        )
        self._diagram_inclusion: InclusionFunctor | None = None
        super().__init__(ambient_category, objects, morphisms)

    def index_set(self) -> MathematicalObject:
        return self._index_set

    def diagram_category(self) -> DiagramCategory:
        return self._diagram_category

    def admit(self, arrow: Arrow) -> Arrow:
        self._diagram_category.admit(arrow)
        return super().admit(arrow)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._diagram_inclusion is None:
            self._diagram_inclusion = InclusionFunctor(
                self,
                self._diagram_category,
            )
        return (self._diagram_inclusion,)


_DIAGRAM_CATEGORIES: dict[int, DiagramCategory] = {}


def is_diagram_category(category: Category) -> TypeIs[DiagramCategory]:
    candidate = _DIAGRAM_CATEGORIES.get(id(category))
    return candidate is category


def is_cone_category(category: Category) -> TypeIs[ConeCategory]:
    from sage_categories.abstract_categories.product_presentations import (
        _CONE_CATEGORIES,
    )

    return any(category is candidate for candidate in _CONE_CATEGORIES.values())


def is_cocone_category(category: Category) -> TypeIs[CoconeCategory]:
    from sage_categories.abstract_categories.product_presentations import (
        _COCONE_CATEGORIES,
    )

    return any(category is candidate for candidate in _COCONE_CATEGORIES.values())


class ConeObject(MathematicalObject):
    """A cone over one diagram."""

    def __init__(
        self,
        *,
        category: ConeCategory,
        apex: MathematicalObject,
        components: Callable[[MathematicalObject], Arrow],
    ) -> None:
        assert apex in category.ambient_category()
        self._apex = apex
        self._components = components
        source = ConstantDiagram(
            category.diagram().domain(),
            category.ambient_category(),
            apex,
        )
        self._transformation = NaturalTransformation(
            source,
            category.diagram(),
            components,
        )
        super().__init__(category=category)

    def diagram(self) -> Functor:
        category = self.category()
        assert is_cone_category(category)
        return category.diagram()

    def apex(self) -> MathematicalObject:
        return self._apex

    def structure_morphism(self, index: MathematicalObject) -> Arrow:
        return self._components(index)

    def transformation(self) -> Arrow:
        return self._transformation


class CoconeObject(MathematicalObject):
    """A cocone under one diagram."""

    def __init__(
        self,
        *,
        category: CoconeCategory,
        apex: MathematicalObject,
        components: Callable[[MathematicalObject], Arrow],
    ) -> None:
        assert apex in category.ambient_category()
        self._apex = apex
        self._components = components
        target = ConstantDiagram(
            category.diagram().domain(),
            category.ambient_category(),
            apex,
        )
        self._transformation = NaturalTransformation(
            category.diagram(),
            target,
            components,
        )
        super().__init__(category=category)

    def diagram(self) -> Functor:
        category = self.category()
        assert is_cocone_category(category)
        return category.diagram()

    def apex(self) -> MathematicalObject:
        return self._apex

    def costructure_morphism(self, index: MathematicalObject) -> Arrow:
        return self._components(index)

    def transformation(self) -> Arrow:
        return self._transformation


class ConeArrow(Arrow):
    """A morphism of cones represented by its apex arrow."""

    def __init__(self, *, hom_category: HomCategory, apex_arrow: Arrow) -> None:
        category = hom_category.base_category()
        assert is_cone_category(category)
        domain = hom_category.domain()
        codomain = hom_category.codomain()
        assert category.contains_cone(domain)
        assert category.contains_cone(codomain)
        assert apex_arrow in category.ambient_category().Hom(
            domain.apex(),
            codomain.apex(),
        )
        self._apex_arrow = apex_arrow
        super().__init__(hom_category=hom_category)

    def apex_arrow(self) -> Arrow:
        return self._apex_arrow


class CoconeArrow(Arrow):
    """A morphism of cocones represented by its apex arrow."""

    def __init__(self, *, hom_category: HomCategory, apex_arrow: Arrow) -> None:
        category = hom_category.base_category()
        assert is_cocone_category(category)
        domain = hom_category.domain()
        codomain = hom_category.codomain()
        assert category.contains_cocone(domain)
        assert category.contains_cocone(codomain)
        assert apex_arrow in category.ambient_category().Hom(
            domain.apex(),
            codomain.apex(),
        )
        self._apex_arrow = apex_arrow
        super().__init__(hom_category=hom_category)

    def apex_arrow(self) -> Arrow:
        return self._apex_arrow


class ConeHomCategory(HomCategory):
    """Morphisms between cones over one diagram."""

    ObjectType = ConeArrow
    ElementType = ConeArrow

    def __call__(self, apex_arrow: Arrow) -> ConeArrow:
        return self.ObjectType(hom_category=self, apex_arrow=apex_arrow)

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> ConeArrow:
        assert value is None
        category = self.base_category()
        assert is_cone_category(category)
        domain = self.domain()
        assert category.contains_cone(domain)
        return self(category.ambient_category().identity(domain.apex()))

    def compose(self, second: Arrow, first: Arrow) -> ConeArrow:
        category = self.base_category()
        assert is_cone_category(category)
        assert category.contains_cone_arrow(second)
        assert category.contains_cone_arrow(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        return self(
            category.ambient_category().compose(
                second.apex_arrow(),
                first.apex_arrow(),
            )
        )

    def contains_cone_arrow(self, arrow: Arrow) -> TypeIs[ConeArrow]:
        return arrow in self


class CoconeHomCategory(HomCategory):
    """Morphisms between cocones under one diagram."""

    ObjectType = CoconeArrow
    ElementType = CoconeArrow

    def __call__(self, apex_arrow: Arrow) -> CoconeArrow:
        return self.ObjectType(hom_category=self, apex_arrow=apex_arrow)

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> CoconeArrow:
        assert value is None
        category = self.base_category()
        assert is_cocone_category(category)
        domain = self.domain()
        assert category.contains_cocone(domain)
        return self(category.ambient_category().identity(domain.apex()))

    def compose(self, second: Arrow, first: Arrow) -> CoconeArrow:
        category = self.base_category()
        assert is_cocone_category(category)
        assert category.contains_cocone_arrow(second)
        assert category.contains_cocone_arrow(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        return self(
            category.ambient_category().compose(
                second.apex_arrow(),
                first.apex_arrow(),
            )
        )

    def contains_cocone_arrow(self, arrow: Arrow) -> TypeIs[CoconeArrow]:
        return arrow in self


class ConeCategory(Category):
    """The category of cones over one diagram."""

    ObjectType = ConeObject

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        super().__init__(object_type=ConeObject)

    def diagram(self) -> Functor:
        return self._diagram

    def ambient_category(self) -> Category:
        return self._diagram.codomain()

    def __call__(
        self,
        apex: MathematicalObject,
        components: Callable[[MathematicalObject], Arrow],
    ) -> ConeObject:
        result = self.ObjectType(category=self, apex=apex, components=components)
        assert self.contains_cone(result)
        return result

    def contains_cone(self, candidate: MathematicalObject) -> TypeIs[ConeObject]:
        return candidate in self

    def contains_cone_arrow(self, candidate: Arrow) -> TypeIs[ConeArrow]:
        return candidate in self.ArrowCategory()

    def _hom_category_type(self) -> type[HomCategory]:
        return ConeHomCategory


class CoconeCategory(Category):
    """The category of cocones under one diagram."""

    ObjectType = CoconeObject

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        super().__init__(object_type=CoconeObject)

    def diagram(self) -> Functor:
        return self._diagram

    def ambient_category(self) -> Category:
        return self._diagram.codomain()

    def __call__(
        self,
        apex: MathematicalObject,
        components: Callable[[MathematicalObject], Arrow],
    ) -> CoconeObject:
        result = self.ObjectType(category=self, apex=apex, components=components)
        assert self.contains_cocone(result)
        return result

    def contains_cocone(self, candidate: MathematicalObject) -> TypeIs[CoconeObject]:
        return candidate in self

    def contains_cocone_arrow(self, candidate: Arrow) -> TypeIs[CoconeArrow]:
        return candidate in self.ArrowCategory()

    def _hom_category_type(self) -> type[HomCategory]:
        return CoconeHomCategory
