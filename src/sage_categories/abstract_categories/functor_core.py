"""Functors and natural transformations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from itertools import pairwise
from typing import TYPE_CHECKING, TypeIs

if TYPE_CHECKING:
    from sage_categories.abstract_categories.product_images import ProductObject
    from sage_categories.abstract_categories.product_presentations import ProductPresentation

from sage_categories.assumptions import AppliedProperty
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
)
from sage_categories.category import Category
from sage_categories.types import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
    registered_element,
)


class Functor(Arrow, ABC):
    """A functor, represented as an arrow in ``Cat``."""

    def __init__(
        self,
        domain: Category,
        codomain: Category,
        *,
        hom_category: HomCategory | None = None,
        object_map: Callable[[MathematicalObject], MathematicalObject] | None = None,
        morphism_map: Callable[[Arrow], Arrow] | None = None,
    ) -> None:
        assert (object_map is None) is (morphism_map is None)
        from sage_categories.abstract_categories.cat import category_universe

        self._cached_image_category: Category | None = None
        self._functor_domain = domain
        self._functor_codomain = codomain
        self._object_map = object_map
        self._morphism_map = morphism_map
        self._object_images: dict[tuple[int, int, int], MathematicalObject] = {}
        self._morphism_images: dict[tuple[int, int, int], Arrow] = {}
        self._object_preimages: dict[
            tuple[int, int, int], MathematicalObject
        ] = {}
        self._morphism_preimages: dict[tuple[int, int, int], Arrow] = {}
        self._postcomposition_functors: dict[int, PostcompositionFunctor] = {}
        functor_hom_category = category_universe(domain, codomain).Hom(domain, codomain) if hom_category is None else hom_category
        assert functor_hom_category.domain() is domain
        assert functor_hom_category.codomain() is codomain
        super().__init__(hom_category=functor_hom_category)

    def domain(self) -> Category:
        """Return the domain category."""
        return self._functor_domain

    def codomain(self) -> Category:
        """Return the codomain category."""
        return self._functor_codomain

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        """Construct the object image."""
        assert self._object_map is not None
        return self._object_map(source)

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        """Construct the arrow image."""
        assert self._morphism_map is not None
        return self._morphism_map(morphism)

    def _canonical_object_source(
        self,
        source: MathematicalObject,
    ) -> MathematicalObject:
        if source.category() is self.domain():
            return source
        if source.category().is_subcategory(self.domain()):
            from sage_categories.compiler import category_compiler

            route = category_compiler().implementation_route(
                source.category(),
                self.domain(),
            )
            return source._object_image_along(route)
        source_element = registered_element(source)
        if source_element is not None and source_element.ambient_object() is self.domain():
            return source
        assert source in self.domain()
        from sage_categories.compiler import category_compiler

        route = category_compiler().implementation_route(
            source.category(),
            self.domain(),
        )
        return source._object_image_along(route)

    def _canonical_morphism_source(self, morphism: Arrow) -> Arrow:
        if morphism.base_category() is self.domain():
            return morphism
        if morphism.base_category().is_subcategory(self.domain()):
            from sage_categories.compiler import category_compiler

            route = category_compiler().implementation_route(
                morphism.base_category(),
                self.domain(),
            )
            return morphism._morphism_image_along(route)
        assert self.domain().contains_arrow(morphism)
        from sage_categories.compiler import category_compiler

        route = category_compiler().implementation_route(
            morphism.base_category(),
            self.domain(),
        )
        return morphism._morphism_image_along(route)

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        """Return the canonical image of one object."""
        original = source
        source = self._canonical_object_source(source)
        key = id(source), id(source), id(self.codomain())
        image = self._object_images.get(key)
        if image is None:
            image = self._object_image(source)
            assert image in self.codomain()
            self._object_images[key] = image
            self._object_preimages[
                (id(source), id(image), id(self.domain()))
            ] = source
        self._object_preimages[
            (id(original), id(image), id(self.domain()))
        ] = original
        return image

    def on_morphism(self, morphism: Arrow) -> Arrow:
        """Return the canonical image of one arrow."""
        original = morphism
        morphism = self._canonical_morphism_source(morphism)
        key = id(morphism.hom_category()), id(morphism), id(self.codomain())
        image = self._morphism_images.get(key)
        if image is None:
            domain = self.on_object(morphism.domain())
            codomain = self.on_object(morphism.codomain())
            image = self._morphism_image(morphism)
            assert self.codomain().contains_arrow(image)
            assert image.domain() is domain
            assert image.codomain() is codomain
            self._morphism_images[key] = image
            self._morphism_preimages[
                (id(morphism.hom_category()), id(image), id(self.domain()))
            ] = morphism
        self._morphism_preimages[
            (id(original.hom_category()), id(image), id(self.domain()))
        ] = original
        return image

    def __call__(self, value: MathematicalObject) -> MathematicalObject:
        """Apply this functor to an object or arrow by categorical membership."""
        arrow_category = self.domain().ArrowCategory()
        if arrow_category.contains_object(value):
            arrow_image = self.on_morphism(value)
            assert arrow_image in self.codomain().ArrowCategory()
            return arrow_image
        assert value in self.domain()
        object_image = self.on_object(value)
        assert object_image in self.codomain()
        return object_image


    def is_full(self) -> AppliedProperty:
        """Return the proposition that this functor is full."""
        return self.hom_category().Full().predicate(self)

    def is_faithful(self) -> AppliedProperty:
        """Return the proposition that this functor is faithful."""
        return self.hom_category().Faithful().predicate(self)

    def is_fully_faithful(self) -> AppliedProperty:
        """Return the proposition that this functor is fully faithful."""
        return self.hom_category().FullyFaithful().predicate(self)

    def is_essentially_surjective(self) -> AppliedProperty:
        """Return the proposition that this functor is essentially surjective."""
        return self.hom_category().EssentiallySurjective().predicate(self)

    def is_equivalence(self) -> AppliedProperty:
        """Return the proposition that this functor is an equivalence."""
        return self.hom_category().Equivalences().predicate(self)

    def factors(self) -> tuple[Functor, ...]:
        return (self,)

    def Image(self) -> Category:
        """Return outputs of this functor with their chosen preimages."""
        if self._cached_image_category is None:
            self._cached_image_category = self._construct_image_category()
        return self._cached_image_category

    def _construct_image_category(self) -> Category:
        from sage_categories.abstract_categories.functor_images import (
            ImageOfFunctor,
        )

        return ImageOfFunctor(self)

    def then(self, following: Functor) -> Functor:
        """Return ``following`` after this functor."""
        return compose_functors(following, self)

    def postcomposition(self, index_category: Category) -> PostcompositionFunctor:
        """Postcompose diagrams of shape ``index_category`` with this functor."""
        key = id(index_category)
        cached = self._postcomposition_functors.get(key)
        if cached is None:
            cached = PostcompositionFunctor(index_category, self)
            self._postcomposition_functors[key] = cached
        return cached


class ConcreteFunctor(Functor, ABC):
    """A functor whose concrete theory also defines an action on elements."""

    def __init__(
        self,
        domain: Category,
        codomain: Category,
        *,
        hom_category: HomCategory | None = None,
    ) -> None:
        self._element_images: dict[
            tuple[int, int, int], MathematicalElement
        ] = {}
        self._element_preimages: dict[
            tuple[int, int, int], MathematicalElement
        ] = {}
        super().__init__(domain, codomain, hom_category=hom_category)

    @abstractmethod
    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        """Construct the element image."""

    def on_element(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        """Return the canonical image of an element of ``source``."""
        original_source = source
        original_element = element
        assert source in self.domain()
        assert element.ambient_object() is source
        if source.category() is not self.domain():
            from sage_categories.compiler import category_compiler

            route = category_compiler().implementation_route(
                source.category(), self.domain()
            )
            source = self._canonical_object_source(source)
            element = element._element_image_along(route)
        target = self.on_object(source)
        key = id(source), id(element), id(self.codomain())
        image = self._element_images.get(key)
        if image is None:
            image = self._element_image(source, element)
            assert image.ambient_object() is target
            self._element_images[key] = image
            self._element_preimages[
                (id(source), id(image), id(self.domain()))
            ] = element
        self._element_preimages[
            (id(original_source), id(image), id(self.domain()))
        ] = original_element
        return image

    def preimage_element(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        """Return the canonical source element represented by ``element``."""
        original_source = source
        normalization_route: tuple[Functor, ...] = ()
        assert source in self.domain()
        if source.category() is not self.domain():
            from sage_categories.compiler import category_compiler

            normalization_route = category_compiler().implementation_route(
                source.category(),
                self.domain(),
            )
            source = self._canonical_object_source(source)
        target = self.on_object(source)
        assert element.ambient_object() is target
        key = id(source), id(element), id(self.domain())
        preimage = self._element_preimages.get(key)
        if preimage is None:
            preimage = self._element_preimage(source, element)
            assert preimage.ambient_object() is source
            self._element_preimages[key] = preimage
        assert preimage.ambient_object() is source
        self._element_images[
            (id(source), id(preimage), id(self.codomain()))
        ] = element
        if normalization_route:
            route_sources: list[MathematicalObject] = [original_source]
            prefix: tuple[Functor, ...] = ()
            for functor in normalization_route[:-1]:
                prefix = (*prefix, functor)
                route_sources.append(original_source._object_image_along(prefix))
            for functor, route_source in reversed(
                tuple(zip(normalization_route, route_sources, strict=True)),
            ):
                assert is_concrete_functor(functor)
                preimage = functor.preimage_element(route_source, preimage)
        assert preimage.ambient_object() is original_source
        self._element_images[
            (id(original_source), id(preimage), id(self.codomain()))
        ] = element
        self._element_preimages[
            (id(original_source), id(element), id(self.domain()))
        ] = preimage
        return preimage

    def preimage_object(
        self,
        source: MathematicalObject,
        image: MathematicalObject,
    ) -> MathematicalObject:
        """Return the source represented by one canonical object image."""
        original_source = source
        assert source in self.domain()
        source = self._canonical_object_source(source)
        assert image is self.on_object(source)
        preimage = self._object_preimages.get(
            (id(original_source), id(image), id(self.domain()))
        )
        if preimage is None:
            preimage = self._object_preimages[
                (id(source), id(image), id(self.domain()))
            ]
        assert preimage is original_source or preimage is source
        return preimage

    def preimage_morphism(self, source: Arrow, image: Arrow) -> Arrow:
        """Return the exact source implementation of a canonical arrow image."""
        assert self.domain().contains_arrow(source)
        assert self.codomain().contains_arrow(image)
        assert self.on_morphism(source) is image
        return self._morphism_preimages[
            (id(source.hom_category()), id(image), id(self.domain()))
        ]

    def _element_preimage(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        from sage_categories.types import TransportedElement

        element_type = self.domain().ElementType
        assert issubclass(element_type, TransportedElement)
        return element_type._transported_from_ambient(
            category=self.domain(),
            ambient_object=source,
            ambient_implementation=element,
        )

    def is_inclusion(self) -> bool:
        """Return whether this functor includes a subcategory."""
        return False

    def _lift_morphism(
        self,
        source: MathematicalObject,
        target: MathematicalObject,
        image: Arrow,
    ) -> Arrow:
        """Construct the canonical source arrow represented by ``image``."""
        from sage_categories.types import TransportedArrow

        assert source in self.domain()
        assert target in self.domain()
        assert image in self.codomain().Hom(
            self.on_object(source),
            self.on_object(target),
        )
        hom_category = self.domain().Hom(source, target)
        preimage_key = id(hom_category), id(image), id(self.domain())
        cached = self._morphism_preimages.get(preimage_key)
        if cached is not None:
            return cached
        arrow_type = hom_category.ObjectType
        assert issubclass(arrow_type, TransportedArrow)
        lifted = arrow_type._transported_from_ambient(
            hom_category=hom_category,
            ambient_implementation=image,
        )
        self._morphism_images[
            (id(lifted.hom_category()), id(lifted), id(self.codomain()))
        ] = image
        self._morphism_preimages[preimage_key] = lifted
        lifted._morphism_structural_images[
            (id(lifted.hom_category()), id(lifted), id(self.codomain()))
        ] = image
        return lifted

    def lift_product(
        self,
        diagram: Functor,
        apex: MathematicalObject,
        inherited_product: ProductPresentation | ProductObject,
    ) -> ProductPresentation:
        """Transport a complete product presentation to ``apex``."""
        from sage_categories.abstract_categories.structural_products import lift_product

        return lift_product(self, diagram, apex, inherited_product)

    def inherited_product(self, diagram: Functor) -> ProductObject:
        """Return the product of the diagram after structural transport."""
        from sage_categories.abstract_categories.structural_products import inherited_product

        return inherited_product(self, diagram)


def is_concrete_functor(
    candidate: MathematicalObject,
) -> TypeIs[ConcreteFunctor]:
    """Return whether ``candidate`` has the concrete-functor element action."""
    return isinstance(candidate, ConcreteFunctor)


class IdentityFunctor(ConcreteFunctor):
    """The identity functor of one category."""

    def __init__(
        self,
        category: Category,
        *,
        hom_category: HomCategory | None = None,
    ) -> None:
        super().__init__(category, category, hom_category=hom_category)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        return source

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        return morphism

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element

    def _element_preimage(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element


    def factors(self) -> tuple[Functor, ...]:
        return ()

    def __repr__(self) -> str:
        return f"Id({self.domain()})"


class RestrictedConcreteFunctor(ConcreteFunctor):
    """The restriction of a structural functor to full subcategories."""

    def __init__(
        self,
        domain: Category,
        codomain: Category,
        ambient_functor: ConcreteFunctor,
    ) -> None:
        from sage_categories.abstract_categories.full_subcategories import (
            is_full_subcategory,
        )

        assert is_full_subcategory(domain)
        assert is_full_subcategory(codomain)
        assert ambient_functor.domain() is domain.ambient_category()
        assert ambient_functor.codomain() is codomain.ambient_category()
        self._source_property = domain
        self._target_property = codomain
        self._ambient_functor = ambient_functor
        super().__init__(domain, codomain)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        ambient_source = self._source_property.inclusion().on_object(source)
        ambient_image = self._ambient_functor.on_object(ambient_source)
        return self._target_property(ambient_image)

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        source = self.on_object(morphism.domain())
        target = self.on_object(morphism.codomain())
        ambient_morphism = self._source_property.inclusion().on_morphism(morphism)
        image = self._ambient_functor.on_morphism(ambient_morphism)
        return self._target_property.Hom(source, target)(image)

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        ambient_source = self._source_property.inclusion().on_object(source)
        ambient_element = self._source_property.inclusion().on_element(
            source,
            element,
        )
        image = self._ambient_functor.on_element(
            ambient_source,
            ambient_element,
        )
        return self._target_property.inclusion().preimage_element(
            self.on_object(source),
            image,
        )

    def _element_preimage(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        target = self.on_object(source)
        ambient_image = self._target_property.inclusion().on_element(
            target,
            element,
        )
        ambient_source = self._source_property.inclusion().on_object(source)
        ambient_element = self._ambient_functor.preimage_element(
            ambient_source,
            ambient_image,
        )
        return self._source_property.inclusion().preimage_element(
            source,
            ambient_element,
        )


    def is_inclusion(self) -> bool:
        return self._ambient_functor.is_inclusion()


class InclusionFunctor(ConcreteFunctor):
    """The identity-on-values inclusion of a subcategory."""

    def __init__(self, domain: Category, codomain: Category) -> None:
        self._included_domain = domain
        super().__init__(domain, codomain)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert source in self._included_domain
        image = source._ambient_implementation()
        assert image in self.codomain()
        return image

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert morphism in self._included_domain.ArrowCategory()
        image = morphism._ambient_implementation()
        assert image in self.codomain().ArrowCategory()
        return image

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        image = element._ambient_implementation()
        assert image.ambient_object() is self.on_object(source)
        return image

    def _element_preimage(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return self._included_domain._refine_element(source, element)


    def is_inclusion(self) -> bool:
        return True


class HomCategoryFamilyInclusionFunctor(ConcreteFunctor):
    """Map each restricted hom category to its ambient hom category."""

    def __init__(
        self,
        domain: HomCategoryFamily,
        codomain: HomCategoryFamily,
    ) -> None:
        self._domain_family = domain
        self._codomain_family = codomain
        super().__init__(domain, codomain)

    def _object_image(self, source: MathematicalObject) -> HomCategory:
        assert self._domain_family.contains_hom_category(source)
        return self._codomain_family.Of(source.domain(), source.codomain())

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert morphism in self._domain_family.ArrowCategory()
        assert morphism in self._codomain_family.ArrowCategory()
        return morphism

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element



class ComposedFunctor(Functor):
    """A flattened nonempty composite of ordinary functors."""

    def __init__(
        self,
        factors: tuple[Functor, ...],
        *,
        hom_category: HomCategory | None = None,
    ) -> None:
        assert factors
        for early, late in pairwise(factors):
            assert early.codomain() is late.domain()
        self._factors = factors
        super().__init__(
            factors[0].domain(),
            factors[-1].codomain(),
            hom_category=hom_category,
        )

    def factors(self) -> tuple[Functor, ...]:
        return self._factors

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        value = source
        for factor in self._factors:
            value = factor.on_object(value)
        return value

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        value = morphism
        for factor in self._factors:
            value = factor.on_morphism(value)
        return value


class ComposedConcreteFunctor(ConcreteFunctor):
    """A composite whose factors all carry concrete element actions."""

    def __init__(
        self,
        factors: tuple[Functor, ...],
        *,
        hom_category: HomCategory | None = None,
    ) -> None:
        assert factors
        for early, late in pairwise(factors):
            assert early.codomain() is late.domain()
        self._factors = factors
        super().__init__(
            factors[0].domain(),
            factors[-1].codomain(),
            hom_category=hom_category,
        )

    def factors(self) -> tuple[Functor, ...]:
        return self._factors

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        value = source
        for factor in self._factors:
            value = factor.on_object(value)
        return value

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        value = morphism
        for factor in self._factors:
            value = factor.on_morphism(value)
        return value

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        current_source = source
        current_element = element
        for factor in self._factors:
            current_element = factor.on_element(current_source, current_element)
            current_source = factor.on_object(current_source)
        return current_element

    def _element_preimage(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        sources: list[MathematicalObject] = [source]
        current_source = source
        for factor in self._factors[:-1]:
            current_source = factor.on_object(current_source)
            sources.append(current_source)
        current_element = element
        for factor, factor_source in reversed(
            tuple(zip(self._factors, sources, strict=True)),
        ):
            current_element = factor.preimage_element(
                factor_source,
                current_element,
            )
        return current_element


def compose_functors(
    second: Functor,
    first: Functor,
    *,
    hom_category: HomCategory | None = None,
) -> Functor:
    """Return the flattened composite ``second`` after ``first``."""
    assert first.codomain() is second.domain()
    factors = first.factors() + second.factors()
    if not factors:
        return IdentityFunctor(first.domain(), hom_category=hom_category)
    if len(factors) == 1:
        return factors[0]
    if all(is_concrete_functor(factor) for factor in factors):
        concrete_factors = tuple(
            factor for factor in factors if is_concrete_functor(factor)
        )
        assert len(concrete_factors) == len(factors)
        return ComposedConcreteFunctor(
            concrete_factors,
            hom_category=hom_category,
        )
    return ComposedFunctor(factors, hom_category=hom_category)


class PostcompositionFunctor(Functor):
    """Postcompose diagrams and right-whisker natural transformations."""

    # This is Mathlib's ``Functor.whiskeringRight`` specialized at one functor:
    # https://github.com/leanprover-community/mathlib4/blob/master/Mathlib/CategoryTheory/Whiskering.lean
    def __init__(self, index_category: Category, functor: Functor) -> None:
        self._index_category = index_category
        self._functor = functor
        super().__init__(
            functor.domain().Diagram(index_category),
            functor.codomain().Diagram(index_category),
        )

    def index_category(self) -> Category:
        return self._index_category

    def functor(self) -> Functor:
        return self._functor

    def _object_image(self, source: MathematicalObject) -> Functor:
        assert is_functor(source)
        return compose_functors(self._functor, source)

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        hom_category = morphism.hom_category()
        assert is_natural_transformation_hom_category(hom_category)
        assert hom_category.contains_transformation(morphism)
        source = self.on_object(morphism.domain())
        target = self.on_object(morphism.codomain())
        assert is_functor(source)
        assert is_functor(target)
        return NaturalTransformation(
            source,
            target,
            lambda index: self._functor.on_morphism(morphism.component(index)),
        )


class DomainFunctor(Functor):
    """The domain functor ``Ar(C) -> C``."""

    def __init__(self, category: Category) -> None:
        self._arrow_domain = category.ArrowCategory()
        super().__init__(self._arrow_domain, category)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._arrow_domain.contains_object(source)
        return source.domain()

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert self._arrow_domain.contains_square(morphism)
        return morphism.left()


class CodomainFunctor(Functor):
    """The codomain functor ``Ar(C) -> C``."""

    def __init__(self, category: Category) -> None:
        self._arrow_domain = category.ArrowCategory()
        super().__init__(self._arrow_domain, category)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._arrow_domain.contains_object(source)
        return source.codomain()

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert self._arrow_domain.contains_square(morphism)
        return morphism.right()


class _NaturalTransformation(Arrow):
    """A natural transformation represented by its object components."""

    def __init__(
        self,
        *,
        hom_category: HomCategory,
        components: Callable[[MathematicalObject], Arrow],
    ) -> None:
        self._components = components
        super().__init__(hom_category=hom_category)

    def component(self, value: MathematicalObject) -> Arrow:
        """Return the component at ``value``."""
        source = self.domain()
        target = self.codomain()
        assert is_functor(source)
        assert is_functor(target)
        assert value in source.domain()
        component = self._components(value)
        assert component in source.codomain().Hom(source(value), target(value))
        return component


class NaturalTransformationHomCategory(HomCategory):
    """Natural transformations between two parallel functors."""

    ObjectType = _NaturalTransformation
    ElementType = _NaturalTransformation

    def __call__(
        self,
        components: Callable[[MathematicalObject], Arrow],
    ) -> _NaturalTransformation:
        return self.ObjectType(hom_category=self, components=components)

    def identity(
        self,
    ) -> _NaturalTransformation:
        source = self.domain()
        assert source is self.codomain()
        assert is_functor(source)
        return self(lambda value: source.codomain().identity(source(value)))

    def compose(self, second: Arrow, first: Arrow) -> _NaturalTransformation:
        second_hom = second.hom_category()
        first_hom = first.hom_category()
        assert is_natural_transformation_hom_category(second_hom)
        assert is_natural_transformation_hom_category(first_hom)
        assert second_hom.contains_transformation(second)
        assert first_hom.contains_transformation(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        return self(lambda value: second.component(value) * first.component(value))

    def contains_transformation(
        self,
        arrow: Arrow,
    ) -> TypeIs[_NaturalTransformation]:
        return arrow in self


class FunctorCategory(HomCategory):
    """The category ``Fun(C, D)`` of functors and natural transformations."""

    ObjectType = Functor
    ElementType = Functor

    def __init__(self, **construction: object) -> None:
        self._functor_properties: dict[str, Category] = {}
        super().__init__(**construction)

    def _property_category(
        self,
        key: str,
        *,
        name: str,
        predicate_name: str,
        implications: Callable[[], tuple[Category, ...]],
    ) -> Category:
        from sage_categories.abstract_categories.functor_properties import (
            FunctorPropertySubcategory,
        )

        category = self._functor_properties.get(key)
        if category is None:
            category = FunctorPropertySubcategory(
                self,
                name=name,
                predicate_name=predicate_name,
                implications=implications,
            )
            self._functor_properties[key] = category
        return category

    def Full(self) -> Category:
        return self._property_category(
            "full", name=f"Full functors in {self}", predicate_name="_full_property",
            implications=lambda: (),
        )

    def Faithful(self) -> Category:
        return self._property_category(
            "faithful", name=f"Faithful functors in {self}",
            predicate_name="_faithful_property", implications=lambda: (),
        )

    def FullyFaithful(self) -> Category:
        return self._property_category(
            "fully_faithful", name=f"Fully faithful functors in {self}",
            predicate_name="_fully_faithful_property",
            implications=lambda: (self.Full(), self.Faithful()),
        )

    def EssentiallySurjective(self) -> Category:
        return self._property_category(
            "essentially_surjective",
            name=f"Essentially surjective functors in {self}",
            predicate_name="_essentially_surjective_property", implications=lambda: (),
        )

    def Equivalences(self) -> Category:
        return self._property_category(
            "equivalence", name=f"Equivalences in {self}",
            predicate_name="_equivalence_property",
            implications=lambda: (self.FullyFaithful(), self.EssentiallySurjective()),
        )

    def __call__(
        self,
        object_map: Callable[[MathematicalObject], MathematicalObject],
        morphism_map: Callable[[Arrow], Arrow],
    ) -> Functor:
        return self.ObjectType(
            self.domain(),
            self.codomain(),
            hom_category=self,
            object_map=object_map,
            morphism_map=morphism_map,
        )

    def _hom_category_type(self) -> type[HomCategory]:
        return NaturalTransformationHomCategory

    def domain(self) -> Category:
        from sage_categories.abstract_categories.cat import is_category_of_categories

        source = HomCategory.domain(self)
        universe = self.base_category()
        assert is_category_of_categories(universe)
        assert universe.contains_category(source)
        return source

    def codomain(self) -> Category:
        from sage_categories.abstract_categories.cat import is_category_of_categories

        target = HomCategory.codomain(self)
        universe = self.base_category()
        assert is_category_of_categories(universe)
        assert universe.contains_category(target)
        return target

    def identity(self) -> Arrow:
        assert self.domain() is self.codomain()
        return IdentityFunctor(self.domain(), hom_category=self)

    def compose(self, second: Arrow, first: Arrow) -> Functor:
        assert is_functor(second)
        assert is_functor(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        return compose_functors(second, first, hom_category=self)

    def contains_functor(self, arrow: Arrow) -> TypeIs[Functor]:
        return arrow in self


def is_functor_category(category: Category) -> TypeIs[FunctorCategory]:
    """Return whether ``category`` is a functor category."""
    from sage_categories.abstract_categories.cat import category_universes

    return any(category in universe.HomCategory() for universe in category_universes())


def is_functor(candidate: MathematicalObject) -> TypeIs[Functor]:
    """Narrow an owned value by membership in ``Ar(Cat)``."""
    from sage_categories.abstract_categories.cat import category_universes

    return any(candidate in universe.ArrowCategory() for universe in category_universes())


def NaturalTransformations(
    source: Functor,
    target: Functor,
) -> NaturalTransformationHomCategory:
    """Return the natural transformations from source to target."""
    assert source.hom_category() is target.hom_category()
    category = source.hom_category().Hom(source, target)
    assert is_natural_transformation_hom_category(category)
    return category


def NaturalTransformation(
    source: Functor,
    target: Functor,
    components: Callable[[MathematicalObject], Arrow],
) -> Arrow:
    """Construct a natural transformation from its components."""
    return NaturalTransformations(source, target)(components)


def NaturalIsomorphism(
    source: Functor,
    target: Functor,
    components: Callable[[MathematicalObject], Arrow],
    inverse_components: Callable[[MathematicalObject], Arrow],
) -> Arrow:
    """Construct a natural isomorphism from inverse component families."""
    from sage_categories.abstract_categories.arrow_categories import (
        declare_isomorphism,
    )

    forward = NaturalTransformation(source, target, components)
    backward = NaturalTransformation(target, source, inverse_components)
    return declare_isomorphism(forward, backward)


def is_natural_transformation_hom_category(
    category: HomCategory,
) -> TypeIs[NaturalTransformationHomCategory]:
    """Return whether ``category`` contains natural transformations."""
    from sage_categories.abstract_categories.cat import category_universes

    base = category.base_category()
    return any(base in universe.HomCategory() for universe in category_universes()) and category in base.HomCategory()
