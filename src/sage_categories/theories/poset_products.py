"""Poset products."""

from __future__ import annotations

from typing import Any, TypeIs

from sage_categories.abstract_categories.arrow_categories import declare_isomorphism
from sage_categories.abstract_categories.functors import (
    Functor,
    NaturalIsomorphism,
    StructuralFunctor,
    compose_functors,
    is_functor,
    is_functor_category,
)
from sage_categories.abstract_categories.hom_categories import (
    Isomorphism,
    is_isomorphism,
)
from sage_categories.abstract_categories.products import (
    ProductLift,
    ProductObject,
    ProductPresentation,
    ProductsOfCategory,
)
from sage_categories.theories.posets import (
    PartiallyOrderedSets,
    PosetElement,
    PosetElements,
    is_poset_hom_category,
)
from sage_categories.theories.sets import (
    ProductElements,
    ProductsOfSetsCategory,
    SetElement,
    SetElements,
    SetObject,
    SetProductObject,
    Sets,
    is_products_of_sets_category,
)
from sage_categories.theories.thin_categories import (
    ThinCategory,
)
from sage_categories.values import (
    UNKNOWN,
    Arrow,
    Decision,
    MathematicalElement,
    MathematicalObject,
    registered_value,
)


class PosetProductObject(ProductObject):
    """A product whose additional order is componentwise."""

    def __init__(
        self,
        *,
        category: ProductsOfPosetsCategory,
        diagram: Functor,
    ) -> None:
        underlying_product = category.set_product(diagram)

        def componentwise(
            left: PosetElement,
            right: PosetElement,
        ) -> Decision:
            left_components = left._set_implementation()
            right_components = right._set_implementation()
            assert ProductElements().contains_product_element(left_components)
            assert ProductElements().contains_product_element(right_components)
            indices = underlying_product.index_set()
            if indices.is_finite() is not True:
                return UNKNOWN
            answer: Decision = True
            for index in indices:
                diagram_object = underlying_product.index_category().object(index)
                factor = diagram(diagram_object)
                assert PartiallyOrderedSets().contains_poset(factor)
                comparison = factor.element(left_components[index]) <= factor.element(
                    right_components[index],
                )
                if comparison is False:
                    return False
                if comparison is UNKNOWN:
                    answer = UNKNOWN
            return answer

        self._underlying_set: SetObject = underlying_product
        self._relation = componentwise
        self._elements: dict[int, PosetElement] = {}
        self._thin_category: ThinCategory | None = None
        MathematicalObject.__init__(self, category=category)
        self._preimage = diagram
        self._image = self
        self._set_product = underlying_product
        self._limit_presentation = self._lifted_product_presentation()

    def _set_implementation(self) -> SetObject:
        return self._underlying_set

    def element(self, set_element: SetElement) -> PosetElement:
        assert set_element.ambient_set() is self._underlying_set
        assert set_element in self._underlying_set
        key = id(set_element)
        cached = self._elements.get(key)
        if cached is None:
            cached = PartiallyOrderedSets().ElementType(
                ambient_object=self,
                set_element=set_element,
            )
            self._elements[key] = cached
        return cached

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return (
            value is not None
            and PosetElements().contains_poset_element(value)
            and value.ambient_poset() is self
        )

    def _is_lequal(self, left: PosetElement, right: PosetElement) -> Decision:
        assert left in self
        assert right in self
        return self._relation(left, right)

    def set_product(self) -> SetProductObject:
        return self._set_product

    def _lifted_product_presentation(self) -> ProductPresentation:
        forgetful = PartiallyOrderedSets().forgetful_functor()
        identity = Sets().identity(self._set_product)
        forward = identity
        backward = identity
        comparison = declare_isomorphism(forward, backward)
        assert is_isomorphism(comparison)

        def lift_morphism(
            source: MathematicalObject,
            target: MathematicalObject,
            underlying: Arrow,
        ) -> Arrow:
            assert PartiallyOrderedSets().contains_poset(source)
            assert PartiallyOrderedSets().contains_poset(target)
            assert Sets().contains_set_morphism(underlying)

            def mapping(member: PosetElement) -> PosetElement:
                set_member = forgetful.on_element(source, member)
                assert SetElements().contains_set_element(set_member)
                return target.element(underlying(set_member))

            return PartiallyOrderedSets().Hom(source, target)(mapping)

        return ProductLift(
            diagram=self.diagram(),
            structural_functor=forgetful,
            inherited_product=self._set_product,
            apex=self,
            comparison=comparison,
            lift_morphism=lift_morphism,
        ).presentation()


class ForgetPosetProductFunctor(StructuralFunctor):
    """Forget componentwise order while retaining the chosen set product."""

    def __init__(self, products: ProductsOfPosetsCategory) -> None:
        self._products = products
        super().__init__(products, products.set_products())

    def _object_image(self, source: MathematicalObject) -> SetProductObject:
        assert self._products.contains_poset_product(source)
        return source.set_product()

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert self._products.contains_image_arrow(morphism)
        underlying = morphism.underlying_arrow()
        underlying_hom = underlying.hom_category()
        assert is_poset_hom_category(underlying_hom)
        assert underlying_hom.contains_poset_morphism(underlying)
        set_morphism = (
            PartiallyOrderedSets()
            .forgetful_functor()
            .on_morphism(
                underlying,
            )
        )
        target = self._products.set_products()
        domain = self.on_object(morphism.domain())
        codomain = self.on_object(morphism.codomain())
        return target.Hom(domain, codomain)(set_morphism)

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> SetElement:
        assert self._products.contains_poset_product(source)
        assert PosetElements().contains_poset_element(element)
        image = (
            PartiallyOrderedSets()
            .forgetful_functor()
            .on_element(
                source,
                element,
            )
        )
        assert SetElements().contains_set_element(image)
        return image

    def is_faithful(self) -> bool:
        return True


class ProductsOfPosetsCategory(ProductsOfCategory):
    """Products of posets with componentwise order."""

    ObjectType: type[PosetProductObject] = PosetProductObject
    ElementType: type[PosetElement] = PosetElement

    def __init__(self, functor: Functor) -> None:
        domain = functor.domain()
        assert is_functor_category(domain)
        self._index_category = domain.domain()
        self._poset_products: dict[int, PosetProductObject] = {}
        self._set_products: ProductsOfSetsCategory | None = None
        self._forgetful_functor: ForgetPosetProductFunctor | None = None
        self._structural_coherence: Isomorphism | None = None
        self._lift_comparison: Isomorphism | None = None
        super().__init__(functor)

    def __call__(self, preimage: MathematicalObject) -> PosetProductObject:
        assert is_functor(preimage)
        return self.product_of(preimage)

    def limit_of(self, diagram: Functor) -> PosetProductObject:
        return self.product_of(diagram)

    def product_of(self, diagram: Functor) -> PosetProductObject:
        assert diagram in self.functor().domain()
        key = id(diagram)
        cached = self._poset_products.get(key)
        if cached is None:
            cached = self.ObjectType(category=self, diagram=diagram)
            self._poset_products[key] = cached
        return cached

    def set_diagram(self, diagram: Functor) -> Functor:
        assert diagram in self.functor().domain()
        image = (
            PartiallyOrderedSets()
            .forgetful_functor()
            .postcomposition(diagram.domain())(diagram)
        )
        assert is_functor(image)
        return image

    def set_products(self) -> ProductsOfSetsCategory:
        if self._set_products is None:
            category = Sets().Products(self._index_category)
            assert is_products_of_sets_category(category)
            self._set_products = category
        return self._set_products

    def set_product(self, diagram: Functor) -> SetProductObject:
        return self.set_products()(self.set_diagram(diagram))

    def forgetful_functor(self) -> ForgetPosetProductFunctor:
        if self._forgetful_functor is None:
            self._forgetful_functor = ForgetPosetProductFunctor(self)
        return self._forgetful_functor

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return (*super().super_functors(), self.forgetful_functor())

    def structural_coherences(self) -> tuple[Isomorphism, ...]:
        if self._structural_coherence is None:
            inclusion = super().super_functors()[0]
            first = compose_functors(
                PartiallyOrderedSets().forgetful_functor(),
                inclusion,
            )
            second = compose_functors(
                self.set_products().inclusion(),
                self.forgetful_functor(),
            )

            def component(source: MathematicalObject) -> Arrow:
                image = first(source)
                assert image is second(source)
                return Sets().identity(image)

            coherence = NaturalIsomorphism(
                second,
                first,
                component,
                component,
            )
            assert is_isomorphism(coherence)
            self._structural_coherence = coherence
        return (self._structural_coherence,)

    def lift_comparisons(self) -> tuple[Isomorphism, ...]:
        if self._lift_comparison is None:
            forgetful = PartiallyOrderedSets().forgetful_functor()
            lifted_product = compose_functors(forgetful, self.functor())
            inherited_product = compose_functors(
                self.set_products().functor(),
                forgetful.postcomposition(self._index_category),
            )

            def component(source: MathematicalObject) -> Arrow:
                assert is_functor(source)
                first = lifted_product(source)
                second = inherited_product(source)
                assert first is second
                return Sets().identity(first)

            comparison = NaturalIsomorphism(
                lifted_product,
                inherited_product,
                component,
                component,
            )
            assert is_isomorphism(comparison)
            self._lift_comparison = comparison
        return (self._lift_comparison,)

    def contains_poset_product(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[PosetProductObject]:
        return candidate in self
