"""Opposite categories and binary products of categories.

The representations follow the research preamble and the standard
constructions in Mathlib's category-theory library.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING, Any, TypeIs, assert_never

from sage_categories.abstract_categories.functors import (
    Functor,
    InclusionFunctor,
    NaturalIsomorphism,
    StructuralFunctor,
    compose_functors,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
    Isomorphism,
    is_isomorphism,
)
from sage_categories.category import Category
from sage_categories.values import (
    Arrow,
    CategoryElement,
    MathematicalElement,
    MathematicalObject,
    registered_value,
)

type ObjectPredicate = Callable[[MathematicalObject], bool]


class BinaryProjectionSide(Enum):
    """One factor of a binary categorical construction."""

    FIRST = "first"
    SECOND = "second"

    def select[Projected](
        self,
        first: Projected,
        second: Projected,
    ) -> Projected:
        match self:
            case BinaryProjectionSide.FIRST:
                return first
            case BinaryProjectionSide.SECOND:
                return second
            case _:
                assert_never(self)


if TYPE_CHECKING:
    from sage_categories.abstract_categories.products import (
        CoconeObject,
        ConeObject,
        CoproductPresentation,
        ProductPresentation,
    )


class OppositeArrow(Arrow):
    """An arrow of an opposite category."""

    def __init__(self, *, hom_category: HomCategory, underlying_arrow: Arrow) -> None:
        opposite = hom_category.base_category()
        assert is_opposite_category(opposite)
        assert underlying_arrow in opposite.base_category().Hom(
            hom_category.codomain(),
            hom_category.domain(),
        )
        self._underlying_arrow = underlying_arrow
        super().__init__(hom_category=hom_category)

    def underlying_arrow(self) -> Arrow:
        return self._underlying_arrow


class OppositeHomCategory(HomCategory):
    """Arrows of an opposite category."""

    ObjectType = OppositeArrow
    ElementType = OppositeArrow

    def __call__(self, underlying_arrow: Arrow) -> OppositeArrow:
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> OppositeArrow:
        assert value is None
        assert self.domain() is self.codomain()
        opposite = self.base_category()
        assert is_opposite_category(opposite)
        return self(opposite.base_category().identity(self.domain()))

    def compose(self, second: Arrow, first: Arrow) -> OppositeArrow:
        assert is_opposite_arrow(second)
        assert is_opposite_arrow(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        opposite = self.base_category()
        assert is_opposite_category(opposite)
        return self(
            opposite.base_category().compose(
                first.underlying_arrow(),
                second.underlying_arrow(),
            )
        )

    def contains_opposite_arrow(self, arrow: Arrow) -> TypeIs[OppositeArrow]:
        return arrow in self


class OppositeCategory(Category):
    """The opposite category ``C^op``."""

    def __init__(self, base_category: Category) -> None:
        self._base_category = base_category
        super().__init__(
            object_type=base_category.ObjectType,
            element_type=base_category.ElementType,
            category=OppositeCategories(),
        )

    def base_category(self) -> Category:
        return self._base_category

    def __contains__(self, candidate: Any) -> bool:
        return candidate in self._base_category

    def _hom_category_type(self) -> type[HomCategory]:
        return OppositeHomCategory

    def OppositeCategory(self) -> Category:
        return self._base_category

    def __repr__(self) -> str:
        return f"{self._base_category}^op"


class CategoryPair(MathematicalObject):
    """An object of a binary product category."""

    def __init__(
        self,
        *,
        category: ProductCategory,
        first: MathematicalObject,
        second: MathematicalObject,
    ) -> None:
        assert first in category.first_category()
        assert second in category.second_category()
        self._first = first
        self._second = second
        super().__init__(category=category)

    def first(self) -> MathematicalObject:
        return self._first

    def second(self) -> MathematicalObject:
        return self._second

    def __repr__(self) -> str:
        return f"({self._first}, {self._second})"


class ProductArrow(Arrow):
    """A pair of arrows in a product category."""

    def __init__(
        self,
        *,
        hom_category: HomCategory,
        first: Arrow,
        second: Arrow,
    ) -> None:
        product = hom_category.base_category()
        assert is_product_category(product)
        domain = hom_category.domain()
        codomain = hom_category.codomain()
        assert product.contains_pair(domain)
        assert product.contains_pair(codomain)
        assert first in product.first_category().Hom(
            domain.first(),
            codomain.first(),
        )
        assert second in product.second_category().Hom(
            domain.second(),
            codomain.second(),
        )
        self._first = first
        self._second = second
        super().__init__(hom_category=hom_category)

    def first(self) -> Arrow:
        return self._first

    def second(self) -> Arrow:
        return self._second


class ProductHomCategory(HomCategory):
    """A hom category in a binary product category."""

    ObjectType = ProductArrow
    ElementType = ProductArrow

    def __call__(self, first: Arrow, second: Arrow) -> ProductArrow:
        return self.ObjectType(hom_category=self, first=first, second=second)

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> ProductArrow:
        assert value is None
        assert self.domain() is self.codomain()
        product = self.base_category()
        assert is_product_category(product)
        domain = self.domain()
        assert product.contains_pair(domain)
        return self(
            product.first_category().identity(domain.first()),
            product.second_category().identity(domain.second()),
        )

    def compose(self, second: Arrow, first: Arrow) -> ProductArrow:
        assert is_product_arrow(second)
        assert is_product_arrow(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        product = self.base_category()
        assert is_product_category(product)
        return self(
            product.first_category().compose(second.first(), first.first()),
            product.second_category().compose(second.second(), first.second()),
        )

    def contains_product_arrow(self, arrow: Arrow) -> TypeIs[ProductArrow]:
        return arrow in self


class ProductCategory(Category):
    """The binary product category ``C x D``."""

    ObjectType = CategoryPair

    def __init__(self, first_category: Category, second_category: Category) -> None:
        self._first_category = first_category
        self._second_category = second_category
        self._pairs: dict[tuple[int, int], CategoryPair] = {}
        self._first_projection: ProductProjectionFunctor | None = None
        self._second_projection: ProductProjectionFunctor | None = None
        super().__init__(
            object_type=CategoryPair,
            element_type=CategoryElement,
            category=ProductCategories(),
        )

    def first_category(self) -> Category:
        return self._first_category

    def second_category(self) -> Category:
        return self._second_category

    def pair(
        self,
        first: MathematicalObject,
        second: MathematicalObject,
    ) -> CategoryPair:
        assert first in self._first_category
        assert second in self._second_category
        key = id(first), id(second)
        cached = self._pairs.get(key)
        if cached is None:
            cached = self.ObjectType(category=self, first=first, second=second)
            self._pairs[key] = cached
        return cached

    def contains_pair(self, candidate: MathematicalObject) -> TypeIs[CategoryPair]:
        return candidate in self

    def __call__(
        self,
        first: MathematicalObject,
        second: MathematicalObject,
    ) -> CategoryPair:
        return self.pair(first, second)

    def _hom_category_type(self) -> type[HomCategory]:
        return ProductHomCategory

    def first_projection(self) -> ProductProjectionFunctor:
        if self._first_projection is None:
            self._first_projection = ProductProjectionFunctor(
                self,
                side=BinaryProjectionSide.FIRST,
            )
        return self._first_projection

    def second_projection(self) -> ProductProjectionFunctor:
        if self._second_projection is None:
            self._second_projection = ProductProjectionFunctor(
                self,
                side=BinaryProjectionSide.SECOND,
            )
        return self._second_projection

    def pair_functor(self, first: Functor, second: Functor) -> PairFunctor:
        return PairFunctor(self, first, second)

    def __repr__(self) -> str:
        return f"{self._first_category} x {self._second_category}"


class ProductProjectionFunctor(Functor):
    """One projection from a binary product category."""

    def __init__(
        self,
        product: ProductCategory,
        *,
        side: BinaryProjectionSide,
    ) -> None:
        self._product = product
        self._side = side
        codomain = side.select(
            product.first_category(),
            product.second_category(),
        )
        super().__init__(product, codomain)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._product.contains_pair(source)
        return self._side.select(source.first(), source.second())

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert is_product_arrow(morphism)
        return self._side.select(morphism.first(), morphism.second())


class PairFunctor(Functor):
    """The functor into a product induced by two functors."""

    def __init__(
        self,
        product: ProductCategory,
        first: Functor,
        second: Functor,
    ) -> None:
        assert first.domain() is second.domain()
        assert first.codomain() is product.first_category()
        assert second.codomain() is product.second_category()
        self._product = product
        self._first = first
        self._second = second
        super().__init__(first.domain(), product)

    def _object_image(self, source: MathematicalObject) -> CategoryPair:
        return self._product(self._first(source), self._second(source))

    def _morphism_image(self, morphism: Arrow) -> ProductArrow:
        source = self.on_object(morphism.domain())
        target = self.on_object(morphism.codomain())
        hom_category = self._product.Hom(source, target)
        assert is_product_hom_category(hom_category)
        first = self._first(morphism)
        second = self._second(morphism)
        assert self._first.codomain().contains_arrow(first)
        assert self._second.codomain().contains_arrow(second)
        return hom_category(first, second)


class PullbackObject(MathematicalObject):
    """A compatible pair of objects in a strict pullback of categories."""

    def __init__(
        self,
        *,
        category: PullbackCategory,
        first: MathematicalObject,
        second: MathematicalObject,
    ) -> None:
        assert first in category.first_category()
        assert second in category.second_category()
        assert category.first_functor()(first) is category.second_functor()(second)
        self._first = first
        self._second = second
        super().__init__(category=category)

    def _first_implementation(self) -> MathematicalObject:
        return self._first

    def _second_implementation(self) -> MathematicalObject:
        return self._second


class PullbackElement(MathematicalElement):
    """A compatible pair of elements in a pullback object."""

    def __init__(
        self,
        *,
        category: PullbackCategory,
        ambient_object: PullbackObject,
        first: MathematicalElement,
        second: MathematicalElement,
    ) -> None:
        assert first.ambient_object() is ambient_object._first_implementation()
        assert second.ambient_object() is ambient_object._second_implementation()
        self._first = first
        self._second = second
        super().__init__(category=category, ambient_object=ambient_object)
        _PULLBACK_ELEMENTS[id(self)] = self

    def _first_implementation(self) -> MathematicalElement:
        return self._first

    def _second_implementation(self) -> MathematicalElement:
        return self._second


class PullbackArrow(Arrow):
    """A compatible pair of arrows in a pullback category."""

    def __init__(
        self,
        *,
        hom_category: HomCategory,
        first: Arrow,
        second: Arrow,
    ) -> None:
        pullback = hom_category.base_category()
        assert is_pullback_category(pullback)
        domain = hom_category.domain()
        codomain = hom_category.codomain()
        assert pullback.contains_pullback_object(domain)
        assert pullback.contains_pullback_object(codomain)
        assert first in pullback.first_category().Hom(
            domain._first_implementation(),
            codomain._first_implementation(),
        )
        assert second in pullback.second_category().Hom(
            domain._second_implementation(),
            codomain._second_implementation(),
        )
        common_first = pullback.first_functor()(first)
        common_second = pullback.second_functor()(second)
        assert pullback.common_category().contains_arrow(common_first)
        assert pullback.common_category().contains_arrow(common_second)
        assert common_first is common_second
        self._first = first
        self._second = second
        super().__init__(hom_category=hom_category)

    def _first_implementation(self) -> Arrow:
        return self._first

    def _second_implementation(self) -> Arrow:
        return self._second


class PullbackHomCategory(HomCategory):
    """Compatible pairs of arrows between pullback objects."""

    ObjectType = PullbackArrow
    ElementType = PullbackArrow

    def __call__(self, first: Arrow, second: Arrow) -> PullbackArrow:
        return self.ObjectType(
            hom_category=self,
            first=first,
            second=second,
        )

    def identity(self, value: MathematicalObject | None = None) -> PullbackArrow:
        assert value is None
        assert self.domain() is self.codomain()
        pullback = self.base_category()
        assert is_pullback_category(pullback)
        domain = self.domain()
        assert pullback.contains_pullback_object(domain)
        return self(
            pullback.first_category().identity(domain._first_implementation()),
            pullback.second_category().identity(domain._second_implementation()),
        )

    def compose(self, second: Arrow, first: Arrow) -> PullbackArrow:
        pullback = self.base_category()
        assert is_pullback_category(pullback)
        assert pullback.contains_pullback_arrow(second)
        assert pullback.contains_pullback_arrow(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        return self(
            pullback.first_category().compose(
                second._first_implementation(),
                first._first_implementation(),
            ),
            pullback.second_category().compose(
                second._second_implementation(),
                first._second_implementation(),
            ),
        )

    def contains_pullback_arrow(self, arrow: Arrow) -> TypeIs[PullbackArrow]:
        return arrow in self


class PullbackProjectionFunctor(StructuralFunctor):
    """One structural projection from a pullback category."""

    def __init__(
        self,
        pullback: PullbackCategory,
        *,
        side: BinaryProjectionSide,
    ) -> None:
        self._pullback = pullback
        self._side = side
        codomain = side.select(
            pullback.first_category(),
            pullback.second_category(),
        )
        super().__init__(pullback, codomain)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._pullback.contains_pullback_object(source)
        return self._side.select(
            source._first_implementation(),
            source._second_implementation(),
        )

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert self._pullback.contains_pullback_arrow(morphism)
        return self._side.select(
            morphism._first_implementation(),
            morphism._second_implementation(),
        )

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        assert self._pullback.contains_pullback_object(source)
        assert self._pullback.contains_pullback_element(element)
        return self._side.select(
            element._first_implementation(),
            element._second_implementation(),
        )


class PullbackMediatingFunctor(Functor):
    """The functor induced by a compatible pair of functors."""

    def __init__(
        self,
        pullback: PullbackCategory,
        first: Functor,
        second: Functor,
    ) -> None:
        assert first.domain() is second.domain()
        assert first.codomain() is pullback.first_category()
        assert second.codomain() is pullback.second_category()
        self._pullback = pullback
        self._first = first
        self._second = second
        super().__init__(first.domain(), pullback)

    def _object_image(self, source: MathematicalObject) -> PullbackObject:
        return self._pullback(self._first(source), self._second(source))

    def _morphism_image(self, morphism: Arrow) -> PullbackArrow:
        source = self.on_object(morphism.domain())
        target = self.on_object(morphism.codomain())
        hom_category = self._pullback.Hom(source, target)
        assert is_pullback_hom_category(hom_category)
        first = self._first(morphism)
        second = self._second(morphism)
        assert self._first.codomain().contains_arrow(first)
        assert self._second.codomain().contains_arrow(second)
        return hom_category(first, second)


class PullbackCategory(Category):
    """The strict pullback of two functors with one codomain."""

    ObjectType = PullbackObject
    ElementType = PullbackElement

    def __init__(
        self,
        first: Functor,
        second: Functor,
        *,
        object_type: type[PullbackObject] | None = None,
        element_type: type[PullbackElement] | None = None,
    ) -> None:
        assert first.codomain() is second.codomain()
        self._first_functor = first
        self._second_functor = second
        self._objects: dict[tuple[int, int], PullbackObject] = {}
        self._first_projection: PullbackProjectionFunctor | None = None
        self._second_projection: PullbackProjectionFunctor | None = None
        self._structural_coherence: Isomorphism | None = None
        super().__init__(
            object_type=object_type,
            element_type=element_type,
            category=PullbackCategories(),
        )

    def first_functor(self) -> Functor:
        return self._first_functor

    def second_functor(self) -> Functor:
        return self._second_functor

    def first_category(self) -> Category:
        return self._first_functor.domain()

    def second_category(self) -> Category:
        return self._second_functor.domain()

    def common_category(self) -> Category:
        return self._first_functor.codomain()

    def __call__(
        self,
        first: MathematicalObject,
        second: MathematicalObject,
    ) -> PullbackObject:
        key = id(first), id(second)
        cached = self._objects.get(key)
        if cached is None:
            cached = self.ObjectType(
                category=self,
                first=first,
                second=second,
            )
            self._objects[key] = cached
        return cached

    def element(
        self,
        source: PullbackObject,
        first: MathematicalElement,
        second: MathematicalElement,
    ) -> PullbackElement:
        return self.ElementType(
            category=self,
            ambient_object=source,
            first=first,
            second=second,
        )

    def contains_pullback_object(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[PullbackObject]:
        return candidate in self

    def contains_pullback_element(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[PullbackElement]:
        value = _PULLBACK_ELEMENTS.get(id(candidate))
        return value is candidate and candidate in self

    def contains_pullback_arrow(self, candidate: Arrow) -> TypeIs[PullbackArrow]:
        return candidate in self.ArrowCategory()

    def _hom_category_type(self) -> type[HomCategory]:
        return PullbackHomCategory

    def first_projection(self) -> PullbackProjectionFunctor:
        if self._first_projection is None:
            self._first_projection = PullbackProjectionFunctor(
                self,
                side=BinaryProjectionSide.FIRST,
            )
        return self._first_projection

    def second_projection(self) -> PullbackProjectionFunctor:
        if self._second_projection is None:
            self._second_projection = PullbackProjectionFunctor(
                self,
                side=BinaryProjectionSide.SECOND,
            )
        return self._second_projection

    def mediating_functor(
        self,
        first: Functor,
        second: Functor,
    ) -> PullbackMediatingFunctor:
        return PullbackMediatingFunctor(self, first, second)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return self.first_projection(), self.second_projection()

    def structural_coherences(self) -> tuple[Isomorphism, ...]:
        if self._structural_coherence is None:
            first = compose_functors(
                self.first_functor(),
                self.first_projection(),
            )
            second = compose_functors(
                self.second_functor(),
                self.second_projection(),
            )

            def component(source: MathematicalObject) -> Arrow:
                image = first(source)
                assert image is second(source)
                return self.common_category().identity(image)

            coherence = NaturalIsomorphism(
                first,
                second,
                component,
                component,
            )
            assert is_isomorphism(coherence)
            self._structural_coherence = coherence
        return (self._structural_coherence,)

    def __repr__(self) -> str:
        return f"{self.first_category()} x_{self.common_category()} {self.second_category()}"


_PULLBACK_ELEMENTS: dict[int, PullbackElement] = {}


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
        return any(isomorphic in self._ambient_category and self._predicate(isomorphic) for isomorphic in _declared_isomorphic_objects(value))

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


class OppositeCategoryObjects(Category):
    """The category of opposite-category objects in ``Cat``."""

    def __init__(self) -> None:
        super().__init__(object_type=OppositeCategory)


class ProductCategoryObjects(Category):
    """The category of binary product-category objects in ``Cat``."""

    def __init__(self) -> None:
        super().__init__(object_type=ProductCategory)


class PullbackCategoryObjects(Category):
    """The category of strict pullback-category objects in ``Cat``."""

    def __init__(self) -> None:
        super().__init__(object_type=PullbackCategory)


class FullSubcategoryObjects(Category):
    """The represented category of full subcategories."""

    def __init__(self) -> None:
        super().__init__(object_type=FullSubcategory)


_OPPOSITE_CATEGORIES = OppositeCategoryObjects()
_PRODUCT_CATEGORIES = ProductCategoryObjects()
_PULLBACK_CATEGORIES = PullbackCategoryObjects()
_FULL_SUBCATEGORIES = FullSubcategoryObjects()


def OppositeCategories() -> OppositeCategoryObjects:
    return _OPPOSITE_CATEGORIES


def ProductCategories() -> ProductCategoryObjects:
    return _PRODUCT_CATEGORIES


def PullbackCategories() -> PullbackCategoryObjects:
    return _PULLBACK_CATEGORIES


def FullSubcategoryCategoryObjects() -> FullSubcategoryObjects:
    return _FULL_SUBCATEGORIES


def is_opposite_category(category: Category) -> TypeIs[OppositeCategory]:
    return category in OppositeCategories()


def is_product_category(category: Category) -> TypeIs[ProductCategory]:
    return category in ProductCategories()


def is_pullback_category(category: Category) -> TypeIs[PullbackCategory]:
    return category in PullbackCategories()


def is_full_subcategory(category: Category) -> TypeIs[FullSubcategory]:
    return category in FullSubcategoryCategoryObjects()


def is_opposite_arrow(arrow: Arrow) -> TypeIs[OppositeArrow]:
    return is_opposite_category(arrow.hom_category().base_category()) and arrow in arrow.hom_category().base_category().ArrowCategory()


def is_opposite_hom_category(
    hom_category: HomCategory,
) -> TypeIs[OppositeHomCategory]:
    opposite = hom_category.base_category()
    return is_opposite_category(opposite) and hom_category is opposite.Hom(
        hom_category.domain(),
        hom_category.codomain(),
    )


def is_product_arrow(arrow: Arrow) -> TypeIs[ProductArrow]:
    return is_product_category(arrow.hom_category().base_category()) and arrow in arrow.hom_category().base_category().ArrowCategory()


def is_product_hom_category(
    hom_category: HomCategory,
) -> TypeIs[ProductHomCategory]:
    product = hom_category.base_category()
    return is_product_category(product) and hom_category is product.Hom(
        hom_category.domain(),
        hom_category.codomain(),
    )


def is_pullback_hom_category(
    hom_category: HomCategory,
) -> TypeIs[PullbackHomCategory]:
    pullback = hom_category.base_category()
    return is_pullback_category(pullback) and hom_category is pullback.Hom(
        hom_category.domain(),
        hom_category.codomain(),
    )
