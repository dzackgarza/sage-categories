"""Full subcategories."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeIs

from sympy.assumptions import AppliedPredicate
from sympy.assumptions.assume import AssumptionsContext
from sympy.assumptions.ask import ask

from sage_categories.abstract_categories.functors import (
    Functor,
    InclusionFunctor,
    StructuralFunctor,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
)
from sage_categories.category import Category
from sage_categories.values import (
    Arrow,
    Decision,
    MathematicalElement,
    MathematicalObject,
    TransportedArrow,
    TransportedElement,
    TransportedObject,
    UNKNOWN,
    registered_element,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.abstract_categories.products import (
        CoconeObject,
        ConeObject,
        CoproductPresentation,
        ProductPresentation,
    )

type ObjectPredicate = Callable[[MathematicalObject], Decision]


class FullSubcategoryObject(TransportedObject):
    """The local object implementation of a full subcategory."""

    def __contains__(self, candidate: Any) -> bool:
        element = registered_element(candidate)
        return element is not None and element.ambient_object() is self


class FullSubcategoryElement(TransportedElement):
    """The local element implementation of a full subcategory."""


class FullSubcategoryArrow(TransportedArrow):
    """The local arrow implementation of a full subcategory."""

    def ambient_implementation(self) -> Arrow:
        return self._ambient_implementation_value


class FullSubcategoryHomCategory(HomCategory):
    """The ambient arrows between two objects of a full subcategory."""

    ObjectType = FullSubcategoryArrow
    ElementType = FullSubcategoryArrow

    def __init__(
        self,
        *,
        domain: MathematicalObject,
        codomain: MathematicalObject,
        hom_category: HomCategoryFamily,
    ) -> None:
        self._ambient_inclusion: StructuralFunctor | None = None
        super().__init__(
            domain=domain,
            codomain=codomain,
            hom_category=hom_category,
        )

    def full_subcategory(self) -> FullSubcategory:
        category = self.base_category()
        assert is_full_subcategory(category)
        return category

    def ambient_hom_category(self) -> HomCategory:
        category = self.full_subcategory()
        inclusion = category.inclusion()
        return category.ambient_category().Hom(
            inclusion.on_object(self.domain()),
            inclusion.on_object(self.codomain()),
        )

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        if value is None:
            return False
        category = self.full_subcategory()
        if not category.contains_arrow(value):
            return False
        ambient = category.ambient_category()
        if value.base_category() is ambient:
            ambient_candidate = value
        elif value.base_category().is_subcategory(ambient):
            from sage_categories.compiler import category_compiler

            route = category_compiler().implementation_route(
                value.base_category(),
                ambient,
            )
            ambient_candidate = value._morphism_image_along(route)
        else:
            return False
        return ambient_candidate in self.ambient_hom_category()

    def __call__(self, arrow: Arrow) -> Arrow:
        assert arrow in self
        ambient = self.full_subcategory().ambient_category()
        if arrow.base_category() is ambient:
            ambient_arrow = arrow
        else:
            from sage_categories.compiler import category_compiler

            route = category_compiler().implementation_route(
                arrow.base_category(),
                ambient,
            )
            ambient_arrow = arrow._morphism_image_along(route)
        return self.full_subcategory()._refine_arrow(self, ambient_arrow)

    def identity(self, value: MathematicalObject | None = None) -> Arrow:
        assert value is None
        assert self.domain() is self.codomain()
        inclusion = self.full_subcategory().inclusion()
        ambient_domain = inclusion.on_object(self.domain())
        return self(inclusion.codomain().identity(ambient_domain))

    def compose(self, second: Arrow, first: Arrow) -> Arrow:
        assert first in self
        assert second in self
        ambient_category = self.full_subcategory().ambient_category()
        return self(
            ambient_category.compose(
                second._ambient_implementation(),
                first._ambient_implementation(),
            )
        )

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._ambient_inclusion is None:
            self._ambient_inclusion = InclusionFunctor(
                self,
                self.ambient_hom_category(),
            )
        return (self._ambient_inclusion,)


class FullSubcategoryHomCategoryFamily(HomCategoryFamily):
    """The hom categories of one full property subcategory."""

    ObjectType: type[FullSubcategoryHomCategory] = FullSubcategoryHomCategory

    def __init__(self, base_category: FullSubcategory) -> None:
        self._full_hom_categories: dict[
            tuple[int, int],
            FullSubcategoryHomCategory,
        ] = {}
        super().__init__(
            base_category,
            hom_category_type=FullSubcategoryHomCategory,
        )

    def Of(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> FullSubcategoryHomCategory:
        base = self.base_category()
        assert domain in base
        assert codomain in base
        key = id(domain), id(codomain)
        cached = self._full_hom_categories.get(key)
        if cached is None:
            cached = self.ObjectType(
                domain=domain,
                codomain=codomain,
                hom_category=self,
            )
            self._full_hom_categories[key] = cached
        return cached


class FullSubcategory(Category):
    """The full subcategory on objects satisfying one predicate."""

    ObjectType: type[MathematicalObject] = FullSubcategoryObject
    ElementType: type[MathematicalElement] = FullSubcategoryElement
    ArrowType: type[Arrow] = FullSubcategoryArrow

    def __init__(
        self,
        ambient_category: Category,
        predicate: ObjectPredicate,
        *,
        name: str,
        object_type: type[MathematicalObject] | None = None,
        element_type: type[MathematicalElement] | None = None,
    ) -> None:
        self._ambient_category = ambient_category
        self._predicate = predicate
        self._name = name
        self._inclusion: InclusionFunctor | None = None
        self._full_hom_category_family: FullSubcategoryHomCategoryFamily | None = None
        super().__init__(
            object_type=object_type,
            element_type=element_type,
            category=FullSubcategoryCategoryObjects(),
        )

    def ambient_category(self) -> Category:
        return self._ambient_category

    def __contains__(self, candidate: Any) -> bool:
        from sage_categories.abstract_categories.hom_categories import (
            _declared_isomorphic_objects,
        )

        value = registered_value(candidate)
        if value is None:
            return False
        category = value.category()
        if category is self or category.is_subcategory(self):
            return True
        if value not in self._ambient_category:
            return False
        return any(
            isomorphic in self._ambient_category
            and self._predicate(isomorphic) is True
            for isomorphic in _declared_isomorphic_objects(value)
        ) or self._predicate(value) is True

    def refine(self, ambient: MathematicalObject) -> MathematicalObject:
        ambient = self._canonical_ambient(ambient)
        assert self._predicate(ambient) is True
        return self._refine_object(ambient)

    def refine_with_hypothesis(
        self,
        ambient: MathematicalObject,
        hypothesis: AppliedPredicate,
        assumptions: AssumptionsContext,
    ) -> MathematicalObject:
        assert ask(hypothesis, context=assumptions) is True
        ambient = self._canonical_ambient(ambient)
        return self._refine_object(ambient)

    def refine_from_theorem(
        self,
        ambient: MathematicalObject,
        owner: MathematicalObject,
    ) -> MathematicalObject:
        assert registered_value(owner) is owner
        ambient = self._canonical_ambient(ambient)
        return self._refine_object(ambient)

    def _canonical_ambient(self, ambient: MathematicalObject) -> MathematicalObject:
        from sage_categories.compiler import category_compiler

        assert ambient in self._ambient_category
        if ambient.category() is self._ambient_category:
            return ambient
        route = category_compiler().implementation_route(
            ambient.category(),
            self._ambient_category,
        )
        return ambient._object_image_along(route)

    def _refine_object(self, ambient: MathematicalObject) -> MathematicalObject:
        from sage_categories.compiler import category_compiler

        if ambient.category() is self:
            assert ambient in self
            return ambient
        ambient = self._canonical_ambient(ambient)
        refined = category_compiler().refine_object(self, ambient)
        assert refined in self
        return refined

    def _refine_element(
        self,
        source: MathematicalObject,
        ambient: MathematicalElement,
    ) -> MathematicalElement:
        from sage_categories.compiler import category_compiler

        assert source in self
        inclusion = self.inclusion()
        ambient_source = inclusion.on_object(source)
        assert ambient.ambient_object() is ambient_source
        return category_compiler().refine_element(self, source, ambient)

    def _refine_arrow(self, hom_category: HomCategory, ambient: Arrow) -> Arrow:
        from sage_categories.compiler import category_compiler

        return category_compiler().refine_arrow(self, hom_category, ambient)

    def contains_arrow(self, candidate: MathematicalObject) -> TypeIs[Arrow]:
        if not self._ambient_category.contains_arrow(candidate):
            return False
        return candidate.domain() in self and candidate.codomain() in self

    def _hom_category_type(self) -> type[HomCategory]:
        return FullSubcategoryHomCategory

    def HomCategory(self) -> FullSubcategoryHomCategoryFamily:
        if self._full_hom_category_family is None:
            self._full_hom_category_family = FullSubcategoryHomCategoryFamily(self)
            self._full_hom_category_family.ElementType = self._compiled_arrow_type
        return self._full_hom_category_family

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> FullSubcategoryHomCategory:
        assert codomain is not None
        return self.HomCategory().Of(domain, codomain)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return (self.inclusion(),)

    def inclusion(self) -> InclusionFunctor:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(self, self._ambient_category)
        return self._inclusion

    def _products_of_category(self, functor: Functor) -> Category:
        return self._ambient_category._products_of_category(functor)

    def _coproducts_of_category(self, functor: Functor) -> Category:
        return self._ambient_category._coproducts_of_category(functor)

    def _limits_of_category(self, functor: Functor) -> Category:
        return self._ambient_category._limits_of_category(functor)

    def _colimits_of_category(self, functor: Functor) -> Category:
        return self._ambient_category._colimits_of_category(functor)

    def chosen_limit(self, diagram: Functor) -> ProductPresentation:
        from sage_categories.abstract_categories.functors import is_functor
        from sage_categories.abstract_categories.products import Cone, Product

        assert diagram.codomain() is self
        ambient_diagram = self.inclusion().postcomposition(diagram.domain())(
            diagram,
        )
        assert is_functor(ambient_diagram)
        ambient_product = self._ambient_category.chosen_limit(ambient_diagram)
        apex = ambient_product.apex()
        assert apex in self

        def projection(index: MathematicalObject) -> Arrow:
            arrow = ambient_product.projection(index)
            assert arrow in self.Hom(apex, diagram(index))
            return arrow

        cone = Cone(diagram, apex, projection)

        def mediate(other: ConeObject) -> Arrow:
            from sage_categories.abstract_categories.products import Cones

            cones = Cones(diagram)
            assert cones.contains_cone(other)
            ambient_cone = Cone(
                ambient_diagram,
                other.apex(),
                other.structure_morphism,
            )
            arrow = ambient_product.universal_morphism(ambient_cone)
            assert arrow in self.Hom(other.apex(), apex)
            return arrow

        return Product(cone, mediate)

    def chosen_colimit(self, diagram: Functor) -> CoproductPresentation:
        from sage_categories.abstract_categories.functors import is_functor
        from sage_categories.abstract_categories.products import Cocone, Coproduct

        assert diagram.codomain() is self
        ambient_diagram = self.inclusion().postcomposition(diagram.domain())(
            diagram,
        )
        assert is_functor(ambient_diagram)
        ambient_coproduct = self._ambient_category.chosen_colimit(
            ambient_diagram,
        )
        apex = ambient_coproduct.apex()
        assert apex in self

        def injection(index: MathematicalObject) -> Arrow:
            arrow = ambient_coproduct.injection(index)
            assert arrow in self.Hom(diagram(index), apex)
            return arrow

        cocone = Cocone(diagram, apex, injection)

        def mediate(other: CoconeObject) -> Arrow:
            from sage_categories.abstract_categories.products import Cocones

            cocones = Cocones(diagram)
            assert cocones.contains_cocone(other)
            ambient_cocone = Cocone(
                ambient_diagram,
                other.apex(),
                other.costructure_morphism,
            )
            arrow = ambient_coproduct.universal_morphism(ambient_cocone)
            assert arrow in self.Hom(apex, other.apex())
            return arrow

        return Coproduct(cocone, mediate)

    def __repr__(self) -> str:
        return self._name


class FullSubcategoryObjects(Category):
    """The represented category of full subcategories."""

    def __init__(self) -> None:
        super().__init__(object_type=FullSubcategory)


_FULL_SUBCATEGORIES = FullSubcategoryObjects()


def FullSubcategoryCategoryObjects() -> FullSubcategoryObjects:
    return _FULL_SUBCATEGORIES


def is_full_subcategory(category: Category) -> TypeIs[FullSubcategory]:
    return category in FullSubcategoryCategoryObjects()
