"""Product presentations."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeIs

from sage_categories.abstract_categories.diagram_shapes import (
    CoconeCategory,
    CoconeObject,
    ConeCategory,
    ConeObject,
)
from sage_categories.abstract_categories.functors import (
    Functor,
    ConcreteFunctor,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    Isomorphism,
    is_isomorphism,
)
from sage_categories.category import Category
from sage_categories.types import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
)

class ProductPresentation(MathematicalObject):
    """A chosen product cone with its universal factorization."""

    def __init__(
        self,
        *,
        category: ProductPresentations,
        cone: ConeObject,
        mediate: Callable[[ConeObject], Arrow],
    ) -> None:
        assert cone in category.cones()
        self._cone = cone
        self._mediate = mediate
        super().__init__(category=category)

    def diagram(self) -> Functor:
        return self._cone.diagram()

    def apex(self) -> MathematicalObject:
        return self._cone.apex()

    def projection(self, index: MathematicalObject) -> Arrow:
        return self._cone.structure_morphism(index)

    def product_cone(self) -> ConeObject:
        return self._cone

    def limit_cone(self) -> ConeObject:
        return self._cone

    def universal_morphism(self, cone: ConeObject) -> Arrow:
        result = self._mediate(cone)
        assert result in self.diagram().codomain().Hom(cone.apex(), self.apex())
        return result


class CoproductPresentation(MathematicalObject):
    """A chosen coproduct cocone with its universal factorization."""

    def __init__(
        self,
        *,
        category: CoproductPresentations,
        cocone: CoconeObject,
        mediate: Callable[[CoconeObject], Arrow],
    ) -> None:
        assert cocone in category.cocones()
        self._cocone = cocone
        self._mediate = mediate
        super().__init__(category=category)

    def diagram(self) -> Functor:
        return self._cocone.diagram()

    def apex(self) -> MathematicalObject:
        return self._cocone.apex()

    def injection(self, index: MathematicalObject) -> Arrow:
        return self._cocone.costructure_morphism(index)

    def coproduct_cocone(self) -> CoconeObject:
        return self._cocone

    def colimit_cocone(self) -> CoconeObject:
        return self._cocone

    def universal_morphism(self, cocone: CoconeObject) -> Arrow:
        result = self._mediate(cocone)
        assert result in self.diagram().codomain().Hom(self.apex(), cocone.apex())
        return result


class BiproductPresentation(MathematicalObject):
    """One object with chosen product and coproduct universal structures."""

    def __init__(
        self,
        *,
        category: BiproductPresentations,
        product: ProductPresentation,
        coproduct: CoproductPresentation,
    ) -> None:
        assert product.diagram() is category.diagram()
        assert coproduct.diagram() is category.diagram()
        assert product.apex() is coproduct.apex()
        self._product = product
        self._coproduct = coproduct
        super().__init__(category=category)

    def diagram(self) -> Functor:
        return self._product.diagram()

    def apex(self) -> MathematicalObject:
        return self._product.apex()

    def projection(self, index: MathematicalObject) -> Arrow:
        return self._product.projection(index)

    def injection(self, index: MathematicalObject) -> Arrow:
        return self._coproduct.injection(index)

    def product_presentation(self) -> ProductPresentation:
        return self._product

    def coproduct_presentation(self) -> CoproductPresentation:
        return self._coproduct


class PresentationArrow(Arrow):
    """A morphism between universal presentations, represented on apexes."""

    def __init__(self, *, hom_category: HomCategory, apex_arrow: Arrow) -> None:
        category = hom_category.base_category()
        assert is_presentation_category(category)
        domain = hom_category.domain()
        codomain = hom_category.codomain()
        assert category.contains_presentation(domain)
        assert category.contains_presentation(codomain)
        assert apex_arrow in category.ambient_category().Hom(
            domain.apex(),
            codomain.apex(),
        )
        self._apex_arrow = apex_arrow
        super().__init__(hom_category=hom_category)

    def apex_arrow(self) -> Arrow:
        return self._apex_arrow


class PresentationHomCategory(HomCategory):
    """Morphisms between universal presentations."""

    ObjectType = PresentationArrow
    ElementType = PresentationArrow

    def __call__(self, apex_arrow: Arrow) -> PresentationArrow:
        return self.ObjectType(hom_category=self, apex_arrow=apex_arrow)

    def identity(
        self,
    ) -> PresentationArrow:
        category = self.base_category()
        assert is_presentation_category(category)
        domain = self.domain()
        assert category.contains_presentation(domain)
        return self(category.ambient_category().identity(domain.apex()))

    def compose(self, second: Arrow, first: Arrow) -> PresentationArrow:
        category = self.base_category()
        assert is_presentation_category(category)
        assert category.contains_presentation_arrow(second)
        assert category.contains_presentation_arrow(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        return self(
            category.ambient_category().compose(
                second.apex_arrow(),
                first.apex_arrow(),
            )
        )

    def contains_presentation_arrow(
        self,
        arrow: Arrow,
    ) -> TypeIs[PresentationArrow]:
        return arrow in self


class ProductApexFunctor(ConcreteFunctor):
    """Send a product presentation to its apex."""

    def __init__(self, domain: ProductPresentations) -> None:
        self._presentations = domain
        super().__init__(domain, domain.ambient_category())

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._presentations.contains_product(source)
        return source.apex()

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert self._presentations.contains_presentation_arrow(morphism)
        return morphism.apex_arrow()

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element


class CoproductApexFunctor(ConcreteFunctor):
    """Send a coproduct presentation to its apex."""

    def __init__(self, domain: CoproductPresentations) -> None:
        self._presentations = domain
        super().__init__(domain, domain.ambient_category())

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._presentations.contains_coproduct(source)
        return source.apex()

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert self._presentations.contains_presentation_arrow(morphism)
        return morphism.apex_arrow()

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element


class BiproductApexFunctor(ConcreteFunctor):
    """Send a biproduct presentation to its common apex."""

    def __init__(self, domain: BiproductPresentations) -> None:
        self._presentations = domain
        super().__init__(domain, domain.ambient_category())

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._presentations.contains_biproduct(source)
        return source.apex()

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert self._presentations.contains_presentation_arrow(morphism)
        return morphism.apex_arrow()

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element


class ProductPresentations(Category):
    """Chosen products of one diagram."""

    ObjectType = ProductPresentation

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        self._apex_functor: ProductApexFunctor | None = None
        super().__init__(object_type=ProductPresentation)

    def diagram(self) -> Functor:
        return self._diagram

    def ambient_category(self) -> Category:
        return self._diagram.codomain()

    def cones(self) -> ConeCategory:
        return Cones(self._diagram)

    def structure_functors(self) -> tuple[Functor, ...]:
        if self._apex_functor is None:
            self._apex_functor = ProductApexFunctor(self)
        return (self._apex_functor,)

    def __call__(
        self,
        cone: ConeObject,
        mediate: Callable[[ConeObject], Arrow],
    ) -> ProductPresentation:
        result = self.ObjectType(category=self, cone=cone, mediate=mediate)
        assert self.contains_product(result)
        return result

    def contains_product(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[ProductPresentation]:
        return candidate in self

    def contains_presentation(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[ProductPresentation]:
        return self.contains_product(candidate)

    def contains_presentation_arrow(
        self,
        candidate: Arrow,
    ) -> TypeIs[PresentationArrow]:
        return candidate in self.ArrowCategory()

    def _hom_category_type(self) -> type[HomCategory]:
        return PresentationHomCategory


class CoproductPresentations(Category):
    """Chosen coproducts of one diagram."""

    ObjectType = CoproductPresentation

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        self._apex_functor: CoproductApexFunctor | None = None
        super().__init__(object_type=CoproductPresentation)

    def diagram(self) -> Functor:
        return self._diagram

    def ambient_category(self) -> Category:
        return self._diagram.codomain()

    def cocones(self) -> CoconeCategory:
        return Cocones(self._diagram)

    def structure_functors(self) -> tuple[Functor, ...]:
        if self._apex_functor is None:
            self._apex_functor = CoproductApexFunctor(self)
        return (self._apex_functor,)

    def __call__(
        self,
        cocone: CoconeObject,
        mediate: Callable[[CoconeObject], Arrow],
    ) -> CoproductPresentation:
        result = self.ObjectType(category=self, cocone=cocone, mediate=mediate)
        assert self.contains_coproduct(result)
        return result

    def contains_coproduct(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[CoproductPresentation]:
        return candidate in self

    def contains_presentation(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[CoproductPresentation]:
        return self.contains_coproduct(candidate)

    def contains_presentation_arrow(
        self,
        candidate: Arrow,
    ) -> TypeIs[PresentationArrow]:
        return candidate in self.ArrowCategory()

    def _hom_category_type(self) -> type[HomCategory]:
        return PresentationHomCategory


class BiproductPresentations(Category):
    """Chosen biproducts of one diagram."""

    ObjectType = BiproductPresentation

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        self._apex_functor: BiproductApexFunctor | None = None
        super().__init__(object_type=BiproductPresentation)

    def diagram(self) -> Functor:
        return self._diagram

    def ambient_category(self) -> Category:
        return self._diagram.codomain()

    def structure_functors(self) -> tuple[Functor, ...]:
        if self._apex_functor is None:
            self._apex_functor = BiproductApexFunctor(self)
        return (self._apex_functor,)

    def __call__(
        self,
        product: ProductPresentation,
        coproduct: CoproductPresentation,
    ) -> BiproductPresentation:
        result = self.ObjectType(
            category=self,
            product=product,
            coproduct=coproduct,
        )
        assert self.contains_biproduct(result)
        return result

    def contains_biproduct(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[BiproductPresentation]:
        return candidate in self

    def contains_presentation(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[BiproductPresentation]:
        return self.contains_biproduct(candidate)

    def contains_presentation_arrow(
        self,
        candidate: Arrow,
    ) -> TypeIs[PresentationArrow]:
        return candidate in self.ArrowCategory()

    def _hom_category_type(self) -> type[HomCategory]:
        return PresentationHomCategory


_CONE_CATEGORIES: dict[int, ConeCategory] = {}

_COCONE_CATEGORIES: dict[int, CoconeCategory] = {}

_PRODUCT_CATEGORIES: dict[int, ProductPresentations] = {}

_COPRODUCT_CATEGORIES: dict[int, CoproductPresentations] = {}

_BIPRODUCT_CATEGORIES: dict[int, BiproductPresentations] = {}


def Cones(diagram: Functor) -> ConeCategory:
    key = id(diagram)
    cached = _CONE_CATEGORIES.get(key)
    if cached is None:
        cached = ConeCategory(diagram)
        _CONE_CATEGORIES[key] = cached
    return cached


def Cocones(diagram: Functor) -> CoconeCategory:
    key = id(diagram)
    cached = _COCONE_CATEGORIES.get(key)
    if cached is None:
        cached = CoconeCategory(diagram)
        _COCONE_CATEGORIES[key] = cached
    return cached


def Products(diagram: Functor) -> ProductPresentations:
    key = id(diagram)
    cached = _PRODUCT_CATEGORIES.get(key)
    if cached is None:
        cached = ProductPresentations(diagram)
        _PRODUCT_CATEGORIES[key] = cached
    return cached


def Coproducts(diagram: Functor) -> CoproductPresentations:
    key = id(diagram)
    cached = _COPRODUCT_CATEGORIES.get(key)
    if cached is None:
        cached = CoproductPresentations(diagram)
        _COPRODUCT_CATEGORIES[key] = cached
    return cached


def Biproducts(diagram: Functor) -> BiproductPresentations:
    key = id(diagram)
    cached = _BIPRODUCT_CATEGORIES.get(key)
    if cached is None:
        cached = BiproductPresentations(diagram)
        _BIPRODUCT_CATEGORIES[key] = cached
    return cached


def Cone(
    diagram: Functor,
    apex: MathematicalObject,
    components: Callable[[MathematicalObject], Arrow],
) -> ConeObject:
    return Cones(diagram)(apex, components)


def Cocone(
    diagram: Functor,
    apex: MathematicalObject,
    components: Callable[[MathematicalObject], Arrow],
) -> CoconeObject:
    return Cocones(diagram)(apex, components)


def Product(
    cone: ConeObject,
    mediate: Callable[[ConeObject], Arrow],
) -> ProductPresentation:
    return Products(cone.diagram())(cone, mediate)


def Coproduct(
    cocone: CoconeObject,
    mediate: Callable[[CoconeObject], Arrow],
) -> CoproductPresentation:
    return Coproducts(cocone.diagram())(cocone, mediate)


def Biproduct(
    product: ProductPresentation,
    coproduct: CoproductPresentation,
) -> BiproductPresentation:
    """Construct a chosen biproduct from compatible product and coproduct presentations."""
    assert product.diagram() is coproduct.diagram()
    assert product.apex() is coproduct.apex()
    return Biproducts(product.diagram())(product, coproduct)


def is_product_presentations(
    category: Category,
) -> TypeIs[ProductPresentations]:
    return any(category is candidate for candidate in _PRODUCT_CATEGORIES.values())


def is_coproduct_presentations(
    category: Category,
) -> TypeIs[CoproductPresentations]:
    return any(category is candidate for candidate in _COPRODUCT_CATEGORIES.values())


def is_biproduct_presentations(
    category: Category,
) -> TypeIs[BiproductPresentations]:
    return any(category is candidate for candidate in _BIPRODUCT_CATEGORIES.values())


def is_presentation_category(
    category: Category,
) -> TypeIs[ProductPresentations | CoproductPresentations | BiproductPresentations]:
    """Return whether ``category`` contains universal presentations."""
    return is_product_presentations(category) or is_coproduct_presentations(category) or is_biproduct_presentations(category)
