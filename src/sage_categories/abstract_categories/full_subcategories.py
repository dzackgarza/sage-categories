"""Full subcategories."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeIs

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
    MathematicalElement,
    MathematicalObject,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.abstract_categories.products import (
        CoconeObject,
        ConeObject,
        CoproductPresentation,
        ProductPresentation,
    )

type ObjectPredicate = Callable[[MathematicalObject], bool]


class FullSubcategoryObject(MathematicalObject):
    """The local object implementation of a full subcategory."""


class FullSubcategoryElement(MathematicalElement):
    """The local element implementation of a full subcategory."""


class FullSubcategoryArrow(Arrow):
    """The local arrow implementation of a full subcategory."""


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
        return category.ambient_category().Hom(self.domain(), self.codomain())

    def __contains__(self, candidate: Any) -> bool:
        return candidate in self.ambient_hom_category()

    def __call__(self, arrow: Arrow) -> Arrow:
        assert arrow in self
        return arrow

    def identity(self, value: MathematicalObject | None = None) -> Arrow:
        assert value is None
        assert self.domain() is self.codomain()
        return self.full_subcategory().ambient_category().identity(self.domain())

    def compose(self, second: Arrow, first: Arrow) -> Arrow:
        assert first in self.full_subcategory().ArrowCategory()
        assert second in self.full_subcategory().ArrowCategory()
        return self.full_subcategory().ambient_category().compose(second, first)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._ambient_inclusion is None:
            self._ambient_inclusion = InclusionFunctor(
                self,
                self.ambient_hom_category(),
            )
        return (self._ambient_inclusion,)


class FullSubcategory(Category):
    """The full subcategory on objects satisfying one predicate."""

    ObjectType: type[MathematicalObject] = FullSubcategoryObject
    ElementType: type[MathematicalElement] = FullSubcategoryElement

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
            isomorphic in self._ambient_category and self._predicate(isomorphic)
            for isomorphic in _declared_isomorphic_objects(value)
        )

    def contains_arrow(self, candidate: MathematicalObject) -> TypeIs[Arrow]:
        if not self._ambient_category.contains_arrow(candidate):
            return False
        return candidate.domain() in self and candidate.codomain() in self

    def _hom_category_type(self) -> type[HomCategory]:
        return FullSubcategoryHomCategory

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
