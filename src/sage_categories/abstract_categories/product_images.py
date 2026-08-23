"""Product images."""

from __future__ import annotations

from typing import TypeIs

from sage_categories.abstract_categories.diagram_shapes import (
    CoconeObject,
    ConeObject,
)
from sage_categories.abstract_categories.functor_images import (
    FunctorImageObject,
    ImageOfFunctor,
)
from sage_categories.abstract_categories.functors import (
    Functor,
)
from sage_categories.abstract_categories.product_presentations import (
    CoproductPresentation,
    ProductPresentation,
    is_coproduct_presentations,
    is_product_presentations,
)
from sage_categories.values import (
    Arrow,
    CategoryElement,
    MathematicalElement,
    MathematicalObject,
)


class LimitObject(FunctorImageObject):
    """A chosen limit with its diagram and universal presentation."""

    def __init__(
        self,
        *,
        category: LimitsOfCategory,
        diagram: Functor,
        presentation: ProductPresentation,
    ) -> None:
        assert presentation.diagram() is diagram
        self._limit_presentation = presentation
        super().__init__(
            category=category,
            preimage=diagram,
            image=presentation.apex(),
        )

    def diagram(self) -> Functor:
        value = self._preimage
        from sage_categories.abstract_categories.functors import is_functor

        assert is_functor(value)
        return value

    def apex(self) -> MathematicalObject:
        """Return the object the limit cone stands over."""
        return self._image

    def limit_cone(self) -> ConeObject:
        return self._limit_presentation.limit_cone()

    def projection(self, index: MathematicalObject) -> Arrow:
        return self._limit_presentation.projection(index)

    def universal_morphism(self, cone: ConeObject) -> Arrow:
        return self._limit_presentation.universal_morphism(cone)


class ColimitObject(FunctorImageObject):
    """A chosen colimit with its diagram and universal presentation."""

    def __init__(
        self,
        *,
        category: ColimitsOfCategory,
        diagram: Functor,
        presentation: CoproductPresentation,
    ) -> None:
        assert presentation.diagram() is diagram
        self._colimit_presentation = presentation
        super().__init__(
            category=category,
            preimage=diagram,
            image=presentation.apex(),
        )

    def diagram(self) -> Functor:
        value = self._preimage
        from sage_categories.abstract_categories.functors import is_functor

        assert is_functor(value)
        return value

    def apex(self) -> MathematicalObject:
        """Return the object the colimit cocone stands under."""
        return self._image

    def colimit_cocone(self) -> CoconeObject:
        return self._colimit_presentation.colimit_cocone()

    def injection(self, index: MathematicalObject) -> Arrow:
        return self._colimit_presentation.injection(index)

    def universal_morphism(self, cocone: CoconeObject) -> Arrow:
        return self._colimit_presentation.universal_morphism(cocone)


class ProductObject(LimitObject):
    """A chosen product of one discrete diagram."""

    def projection(self, index: MathematicalObject) -> Arrow:
        return self._limit_presentation.projection(index)


class CoproductObject(ColimitObject):
    """A chosen coproduct of one discrete diagram."""

    def injection(self, index: MathematicalObject) -> Arrow:
        return self._colimit_presentation.injection(index)


class LimitsOfCategory(ImageOfFunctor):
    """Chosen limits constructed by one limit functor."""

    ObjectType: type[LimitObject] = LimitObject
    ElementType: type[MathematicalElement] = CategoryElement

    def __init__(
        self,
        functor: Functor,
        *,
        object_type: type[LimitObject] | None = None,
        element_type: type[MathematicalElement] | None = None,
    ) -> None:
        self._limits: dict[int, LimitObject] = {}
        super().__init__(
            functor,
            object_type=object_type,
            element_type=element_type,
        )
        _LIMIT_IMAGE_CATEGORIES[id(self)] = self

    def __call__(self, preimage: MathematicalObject) -> LimitObject:
        presentation_category = preimage.category()
        if is_product_presentations(presentation_category):
            assert presentation_category.contains_product(preimage)
            return self._limit_from_presentation(preimage)
        from sage_categories.abstract_categories.functors import is_functor

        assert is_functor(preimage)
        return self.limit_of(preimage)

    def limit_of(self, diagram: Functor) -> LimitObject:
        assert diagram in self.functor().domain()
        key = id(diagram)
        cached = self._limits.get(key)
        if cached is None:
            presentation = self.functor().codomain().chosen_limit(diagram)
            cached = self._limit_from_presentation(presentation)
        return cached

    def _limit_from_presentation(
        self,
        presentation: ProductPresentation,
    ) -> LimitObject:
        diagram = presentation.diagram()
        assert diagram in self.functor().domain()
        assert presentation.apex() in self.functor().codomain()
        key = id(diagram)
        cached = self._limits.get(key)
        if cached is None:
            candidate = self.ObjectType(
                category=self,
                diagram=diagram,
                presentation=presentation,
            )
            assert self.contains_limit(candidate)
            cached = candidate
            self._limits[key] = cached
        return cached

    def contains_limit(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[LimitObject]:
        return candidate in self


class ColimitsOfCategory(ImageOfFunctor):
    """Chosen colimits constructed by one colimit functor."""

    ObjectType: type[ColimitObject] = ColimitObject
    ElementType: type[MathematicalElement] = CategoryElement

    def __init__(
        self,
        functor: Functor,
        *,
        object_type: type[ColimitObject] | None = None,
        element_type: type[MathematicalElement] | None = None,
    ) -> None:
        self._colimits: dict[int, ColimitObject] = {}
        super().__init__(
            functor,
            object_type=object_type,
            element_type=element_type,
        )
        _COLIMIT_IMAGE_CATEGORIES[id(self)] = self

    def __call__(self, preimage: MathematicalObject) -> ColimitObject:
        presentation_category = preimage.category()
        if is_coproduct_presentations(presentation_category):
            assert presentation_category.contains_coproduct(preimage)
            return self._colimit_from_presentation(preimage)
        from sage_categories.abstract_categories.functors import is_functor

        assert is_functor(preimage)
        return self.colimit_of(preimage)

    def colimit_of(self, diagram: Functor) -> ColimitObject:
        assert diagram in self.functor().domain()
        key = id(diagram)
        cached = self._colimits.get(key)
        if cached is None:
            presentation = self.functor().codomain().chosen_colimit(diagram)
            cached = self._colimit_from_presentation(presentation)
        return cached

    def _colimit_from_presentation(
        self,
        presentation: CoproductPresentation,
    ) -> ColimitObject:
        diagram = presentation.diagram()
        assert diagram in self.functor().domain()
        assert presentation.apex() in self.functor().codomain()
        key = id(diagram)
        cached = self._colimits.get(key)
        if cached is None:
            candidate = self.ObjectType(
                category=self,
                diagram=diagram,
                presentation=presentation,
            )
            assert self.contains_colimit(candidate)
            cached = candidate
            self._colimits[key] = cached
        return cached

    def contains_colimit(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[ColimitObject]:
        return candidate in self


class ProductsOfCategory(LimitsOfCategory):
    """Chosen products constructed by one product functor."""

    def __init__(
        self,
        functor: Functor,
        *,
        object_type: type[ProductObject] | None = None,
        element_type: type[MathematicalElement] | None = None,
    ) -> None:
        super().__init__(
            functor,
            object_type=object_type,
            element_type=element_type,
        )
        _PRODUCT_IMAGE_CATEGORIES[id(self)] = self

    def __call__(self, preimage: MathematicalObject) -> ProductObject:
        product = super().__call__(preimage)
        assert self.contains_product(product)
        return product

    def product_of(self, diagram: Functor) -> ProductObject:
        product = self.limit_of(diagram)
        assert self.contains_product(product)
        return product

    def contains_product(self, value: MathematicalObject) -> TypeIs[ProductObject]:
        return value in self


class CoproductsOfCategory(ColimitsOfCategory):
    """Chosen coproducts constructed by one coproduct functor."""

    def __init__(
        self,
        functor: Functor,
        *,
        object_type: type[CoproductObject] | None = None,
        element_type: type[MathematicalElement] | None = None,
    ) -> None:
        super().__init__(
            functor,
            object_type=object_type,
            element_type=element_type,
        )
        _COPRODUCT_IMAGE_CATEGORIES[id(self)] = self

    def __call__(self, preimage: MathematicalObject) -> CoproductObject:
        coproduct = super().__call__(preimage)
        assert self.contains_coproduct(coproduct)
        return coproduct

    def coproduct_of(self, diagram: Functor) -> CoproductObject:
        coproduct = self.colimit_of(diagram)
        assert self.contains_coproduct(coproduct)
        return coproduct

    def contains_coproduct(
        self,
        value: MathematicalObject,
    ) -> TypeIs[CoproductObject]:
        return value in self


_LIMIT_IMAGE_CATEGORIES: dict[int, LimitsOfCategory] = {}

_COLIMIT_IMAGE_CATEGORIES: dict[int, ColimitsOfCategory] = {}

_PRODUCT_IMAGE_CATEGORIES: dict[int, ProductsOfCategory] = {}

_COPRODUCT_IMAGE_CATEGORIES: dict[int, CoproductsOfCategory] = {}


def is_limits_of_category(category: Category) -> TypeIs[LimitsOfCategory]:
    candidate = _LIMIT_IMAGE_CATEGORIES.get(id(category))
    return candidate is category


def is_colimits_of_category(category: Category) -> TypeIs[ColimitsOfCategory]:
    candidate = _COLIMIT_IMAGE_CATEGORIES.get(id(category))
    return candidate is category


def is_products_of_category(category: Category) -> TypeIs[ProductsOfCategory]:
    candidate = _PRODUCT_IMAGE_CATEGORIES.get(id(category))
    return candidate is category


def is_coproducts_of_category(
    category: Category,
) -> TypeIs[CoproductsOfCategory]:
    candidate = _COPRODUCT_IMAGE_CATEGORIES.get(id(category))
    return candidate is category
