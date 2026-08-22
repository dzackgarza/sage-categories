"""Categories as objects of ``Cat``.

This is the runtime-independent form of the architecture in
``abstract_categories/cat.sage`` from the research preamble.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, TypeIs

from sage_categories.compiler import DeclaredMethod, category_compiler
from sage_categories.values import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
    MembershipInput,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.abstract_categories.arrow_categories import (
        ArrowCategory as ArrowCategoryObject,
    )
    from sage_categories.abstract_categories.functors import (
        Functor,
        StructuralFunctor,
    )
    from sage_categories.abstract_categories.hom_categories import (
        HomCategory as HomCategoryObject,
    )
    from sage_categories.abstract_categories.hom_categories import (
        HomCategoryFamily,
    )
    from sage_categories.abstract_categories.products import (
        ColimitObject,
        CoproductPresentation,
        LimitObject,
        ProductPresentation,
    )
    from sage_categories.abstract_categories.slice_categories import (
        CosliceUnderCategory,
        CoveredObjectCategory,
        CoveringObjectCategory,
        SliceOverCategory,
        SubobjectCategory,
        SuperobjectCategory,
    )


class Category(MathematicalObject):
    """A category with category-owned object and element implementations."""

    ObjectType: type[MathematicalObject]
    ElementType: type[MathematicalElement]

    def __init__(
        self,
        *,
        object_type: type[MathematicalObject] = MathematicalObject,
        element_type: type[MathematicalElement] = MathematicalElement,
        category: Category | None = None,
    ) -> None:
        if category is None:
            from sage_categories.abstract_categories.cat import Cat

            category = Cat()
        super().__init__(category=category)
        self._initialize_category(object_type, element_type)

    def _initialize_category(
        self,
        object_type: type[MathematicalObject],
        element_type: type[MathematicalElement],
    ) -> None:
        self._local_object_type = object_type
        self._local_element_type = element_type
        self._hom_category_family: HomCategoryFamily | None = None
        self._arrow_category: ArrowCategoryObject | None = None
        self._end_arrow_category: Category | None = None
        self._mono_arrow_category: Category | None = None
        self._epi_arrow_category: Category | None = None
        self._iso_arrow_category: Category | None = None
        self._aut_arrow_category: Category | None = None
        self._opposite_category: Category | None = None
        self._product_categories: dict[int, Category] = {}
        self._wide_subcategories: dict[int, Category] = {}
        self._limit_functors: dict[int, Functor] = {}
        self._colimit_functors: dict[int, Functor] = {}
        self._product_functors: dict[int, Functor] = {}
        self._coproduct_functors: dict[int, Functor] = {}
        self._slice_over_categories: dict[int, SliceOverCategory] = {}
        self._coslice_under_categories: dict[int, CosliceUnderCategory] = {}
        self._subobject_categories: dict[int, SubobjectCategory] = {}
        self._superobject_categories: dict[int, SuperobjectCategory] = {}
        self._covering_object_categories: dict[int, CoveringObjectCategory] = {}
        self._covered_object_categories: dict[int, CoveredObjectCategory] = {}
        self._end_category: HomCategoryFamily | None = None
        self._mono_category: HomCategoryFamily | None = None
        self._epi_category: HomCategoryFamily | None = None
        self._iso_category: HomCategoryFamily | None = None
        self._aut_category: HomCategoryFamily | None = None
        compiler = category_compiler()
        self.ObjectType = compiler.compiled_object_type(self, object_type)
        self.ElementType = compiler.compiled_element_type(self, element_type)

    def local_object_type(self) -> type[MathematicalObject]:
        """Return the object implementation declared at this category."""
        return self._local_object_type

    def local_element_type(self) -> type[MathematicalElement]:
        """Return the element implementation declared at this category."""
        return self._local_element_type

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        """Return functors selected for implicit implementation inheritance."""
        return ()

    def super_categories(self) -> tuple[Category, ...]:
        """Return the category graph derived from structural functors."""
        return tuple(functor.codomain() for functor in self.super_functors())

    def is_subcategory(self, category: Category) -> bool:
        """Return whether the structural-functor graph includes ``category``."""
        if self is category:
            return True
        return any(codomain is category or codomain.is_subcategory(category) for codomain in self.super_categories())

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        return value is not None and value._belongs_to(self)

    def contains_arrow(self, candidate: MathematicalObject) -> TypeIs[Arrow]:
        """Return whether ``candidate`` is an arrow of this category."""
        return candidate._is_arrow_in(self)

    def objects(self) -> MathematicalObject:
        """Return the object set when this category is represented as small."""
        assert False, f"{self} has no represented object set"

    def arrows(self) -> MathematicalObject:
        """Return the arrow set when this category is represented as small."""
        assert False, f"{self} has no represented arrow set"

    def _belongs_to(self, category: Category) -> bool:
        from sage_categories.abstract_categories.cat import Cat

        if category is Cat():
            return self is not category
        return super()._belongs_to(category)

    def _hom_category_type(self) -> type[HomCategoryObject]:
        from sage_categories.abstract_categories.hom_categories import HomCategory

        return HomCategory

    def _hom_category_family_type(self) -> type[HomCategoryFamily]:
        from sage_categories.abstract_categories.hom_categories import (
            HomCategoryFamily,
        )

        return HomCategoryFamily

    def HomCategory(self) -> HomCategoryFamily:
        """Return the category of hom categories of this category."""
        if self._hom_category_family is None:
            family_type = self._hom_category_family_type()
            self._hom_category_family = family_type(
                self,
                hom_category_type=self._hom_category_type(),
            )
        return self._hom_category_family

    def EndCategory(self) -> HomCategoryFamily:
        """Return the category of endomorphism categories."""
        if self._end_category is None:
            from sage_categories.abstract_categories.hom_categories import (
                EndCategoryFamily,
            )

            self._end_category = EndCategoryFamily(self)
        return self._end_category

    def MonoCategory(self) -> HomCategoryFamily:
        """Return the category of monomorphism categories."""
        if self._mono_category is None:
            from sage_categories.abstract_categories.hom_categories import (
                MonomorphismCategoryFamily,
            )

            self._mono_category = MonomorphismCategoryFamily(self)
        return self._mono_category

    def EpiCategory(self) -> HomCategoryFamily:
        """Return the category of epimorphism categories."""
        if self._epi_category is None:
            from sage_categories.abstract_categories.hom_categories import (
                EpimorphismCategoryFamily,
            )

            self._epi_category = EpimorphismCategoryFamily(self)
        return self._epi_category

    def IsoCategory(self) -> HomCategoryFamily:
        """Return the category of isomorphism categories."""
        if self._iso_category is None:
            from sage_categories.abstract_categories.hom_categories import (
                IsomorphismCategoryFamily,
            )

            self._iso_category = IsomorphismCategoryFamily(self)
        return self._iso_category

    def AutCategory(self) -> HomCategoryFamily:
        """Return the category of automorphism categories."""
        if self._aut_category is None:
            from sage_categories.abstract_categories.hom_categories import (
                AutomorphismCategoryFamily,
            )

            self._aut_category = AutomorphismCategoryFamily(self)
        return self._aut_category

    @property
    def HomCatType(self) -> type[HomCategoryObject]:
        return self.HomCategory().ObjectType

    @property
    def EndCatType(self) -> type[HomCategoryObject]:
        return self.EndCategory().ObjectType

    @property
    def MonoCatType(self) -> type[HomCategoryObject]:
        return self.MonoCategory().ObjectType

    @property
    def EpiCatType(self) -> type[HomCategoryObject]:
        return self.EpiCategory().ObjectType

    @property
    def IsoCatType(self) -> type[HomCategoryObject]:
        return self.IsoCategory().ObjectType

    @property
    def AutCatType(self) -> type[HomCategoryObject]:
        return self.AutCategory().ObjectType

    @property
    def ArrowType(self) -> type[Arrow]:
        """Return the arrow type as ``HomCatType.ElementType``."""
        return self.HomCatType.ElementType

    @property
    def EndArrowType(self) -> type[Arrow]:
        return self.EndCatType.ElementType

    @property
    def MonoArrowType(self) -> type[Arrow]:
        return self.MonoCatType.ElementType

    @property
    def EpiArrowType(self) -> type[Arrow]:
        return self.EpiCatType.ElementType

    @property
    def IsoArrowType(self) -> type[Arrow]:
        return self.IsoCatType.ElementType

    @property
    def AutArrowType(self) -> type[Arrow]:
        return self.AutCatType.ElementType

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> HomCategoryObject:
        """Return ``Hom_C(domain, codomain)``."""
        if codomain is None:
            return MathematicalObject.Hom(self, domain)
        assert domain in self and codomain in self
        return self.HomCategory().Of(domain, codomain)

    def End(self, value: MathematicalObject | None = None) -> HomCategoryObject:
        """Return ``End_C(value)``."""
        if value is None:
            return MathematicalObject.End(self)
        assert value in self
        return self.EndCategory().Of(value, value)

    def Mono(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> HomCategoryObject:
        """Return the monomorphisms from domain to codomain."""
        if codomain is None:
            return MathematicalObject.Mono(self, domain)
        return self.MonoCategory().Of(domain, codomain)

    def Epi(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> HomCategoryObject:
        """Return the epimorphisms from domain to codomain."""
        if codomain is None:
            return MathematicalObject.Epi(self, domain)
        return self.EpiCategory().Of(domain, codomain)

    def Iso(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> HomCategoryObject:
        """Return the isomorphisms from domain to codomain."""
        if codomain is None:
            return MathematicalObject.Iso(self, domain)
        return self.IsoCategory().Of(domain, codomain)

    def Aut(self, value: MathematicalObject | None = None) -> HomCategoryObject:
        """Return the automorphisms of ``value``."""
        if value is None:
            return MathematicalObject.Aut(self)
        return self.AutCategory().Of(value, value)

    def identity(self, value: MathematicalObject | None = None) -> Arrow:
        """Return the identity arrow of ``value``."""
        if value is None:
            return MathematicalObject.identity(self)
        return self.Aut(value).identity()

    def compose(self, second: Arrow, first: Arrow) -> Arrow:
        """Return ``second`` after ``first``."""
        assert first in self.ArrowCategory()
        assert second in self.ArrowCategory()
        assert first.codomain() is second.domain()
        return self.Hom(first.domain(), second.codomain()).compose(second, first)

    def ArrowCategory(self) -> ArrowCategoryObject:
        """Return ``Ar(C)``."""
        if self._arrow_category is None:
            from sage_categories.abstract_categories.arrow_categories import (
                ArrowCategory,
            )

            self._arrow_category = ArrowCategory(self)
        return self._arrow_category

    def EndArrowCategory(self) -> Category:
        """Return the full subcategory of ``Ar(C)`` on endomorphisms."""
        if self._end_arrow_category is None:
            from sage_categories.abstract_categories.arrow_categories import (
                EndArrowCategory,
            )

            self._end_arrow_category = EndArrowCategory(self)
        return self._end_arrow_category

    def MonomorphismArrowCategory(self) -> Category:
        """Return the subcategory of ``Ar(C)`` on monomorphisms."""
        if self._mono_arrow_category is None:
            from sage_categories.abstract_categories.arrow_categories import (
                MonomorphismArrowCategory,
            )

            self._mono_arrow_category = MonomorphismArrowCategory(self)
        return self._mono_arrow_category

    def EpimorphismArrowCategory(self) -> Category:
        """Return the subcategory of ``Ar(C)`` on epimorphisms."""
        if self._epi_arrow_category is None:
            from sage_categories.abstract_categories.arrow_categories import (
                EpimorphismArrowCategory,
            )

            self._epi_arrow_category = EpimorphismArrowCategory(self)
        return self._epi_arrow_category

    def IsomorphismArrowCategory(self) -> Category:
        """Return the subcategory of ``Ar(C)`` on isomorphisms."""
        if self._iso_arrow_category is None:
            from sage_categories.abstract_categories.arrow_categories import (
                IsomorphismArrowCategory,
            )

            self._iso_arrow_category = IsomorphismArrowCategory(self)
        return self._iso_arrow_category

    def AutomorphismArrowCategory(self) -> Category:
        """Return the full subcategory of ``Ar(C)`` on automorphisms."""
        if self._aut_arrow_category is None:
            from sage_categories.abstract_categories.arrow_categories import (
                AutomorphismArrowCategory,
            )

            self._aut_arrow_category = AutomorphismArrowCategory(self)
        return self._aut_arrow_category

    def core(self) -> Category:
        """Return the maximal subgroupoid of this category."""
        return self.WideSubcategory(self.IsomorphismArrowCategory())

    def WideSubcategory(self, arrows: Category) -> Category:
        """Keep all objects and restrict the arrows to ``arrows``."""
        from sage_categories.abstract_categories.arrow_categories import (
            WideSubcategory,
        )

        key = id(arrows)
        cached = self._wide_subcategories.get(key)
        if cached is None:
            cached = WideSubcategory(self, arrows)
            self._wide_subcategories[key] = cached
        return cached

    def DomainFunctor(self) -> Functor:
        """Return ``dom: Ar(C) -> C``."""
        from sage_categories.abstract_categories.functors import DomainFunctor

        return DomainFunctor(self)

    def CodomainFunctor(self) -> Functor:
        """Return ``cod: Ar(C) -> C``."""
        from sage_categories.abstract_categories.functors import CodomainFunctor

        return CodomainFunctor(self)

    def FunctorCategory(self, codomain: Category) -> HomCategoryObject:
        """Return the functor category from this category to ``codomain``."""
        from sage_categories.abstract_categories.cat import Cat

        return Cat().Hom(self, codomain)

    def Diagram(self, index_category: Category) -> HomCategoryObject:
        """Return the category of diagrams of shape ``index_category``."""
        return index_category.FunctorCategory(self)

    def DiagonalFunctor(self, index_category: Category) -> Functor:
        """Return the diagonal functor into diagrams of one shape."""
        from sage_categories.abstract_categories.functors import DiagonalFunctor

        return DiagonalFunctor(self, index_category)

    def LimitFunctor(self, index_category: Category) -> Functor:
        """Return the chosen limit functor on diagrams of one shape."""
        from sage_categories.abstract_categories.functors import LimitFunctor

        key = id(index_category)
        cached = self._limit_functors.get(key)
        if cached is None:
            cached = LimitFunctor(self, index_category)
            self._limit_functors[key] = cached
        return cached

    def Limits(self, index_category: Category) -> Category:
        """Return the image category of one chosen limit functor."""
        return self.LimitFunctor(index_category).Image()

    def ColimitFunctor(self, index_category: Category) -> Functor:
        """Return the chosen colimit functor on diagrams of one shape."""
        from sage_categories.abstract_categories.functors import ColimitFunctor

        key = id(index_category)
        cached = self._colimit_functors.get(key)
        if cached is None:
            cached = ColimitFunctor(self, index_category)
            self._colimit_functors[key] = cached
        return cached

    def Colimits(self, index_category: Category) -> Category:
        """Return the image category of one chosen colimit functor."""
        return self.ColimitFunctor(index_category).Image()

    def ProductFunctor(self, index_category: Category) -> Functor:
        """Return the chosen product functor on discrete diagrams."""
        from sage_categories.abstract_categories.functors import ProductFunctor

        key = id(index_category)
        cached = self._product_functors.get(key)
        if cached is None:
            cached = ProductFunctor(self, index_category)
            self._product_functors[key] = cached
        return cached

    def Products(self, index_category: Category) -> Category:
        """Return the image category of one chosen product functor."""
        return self.ProductFunctor(index_category).Image()

    def CoproductFunctor(self, index_category: Category) -> Functor:
        """Return the chosen coproduct functor on discrete diagrams."""
        from sage_categories.abstract_categories.functors import CoproductFunctor

        key = id(index_category)
        cached = self._coproduct_functors.get(key)
        if cached is None:
            cached = CoproductFunctor(self, index_category)
            self._coproduct_functors[key] = cached
        return cached

    def Coproducts(self, index_category: Category) -> Category:
        """Return the image category of one chosen coproduct functor."""
        return self.CoproductFunctor(index_category).Image()

    def chosen_limit(self, diagram: Functor) -> ProductPresentation:
        """Return the chosen limit presentation of ``diagram``."""
        assert diagram.codomain() is self
        assert False, f"{self} does not define chosen limits"

    def chosen_colimit(self, diagram: Functor) -> CoproductPresentation:
        """Return the chosen colimit presentation of ``diagram``."""
        assert diagram.codomain() is self
        assert False, f"{self} does not define chosen colimits"

    def equalizer(self, first: Arrow, second: Arrow) -> LimitObject:
        """Return the chosen equalizer of two parallel arrows."""
        from sage_categories.abstract_categories.functors import InclusionFunctor
        from sage_categories.abstract_categories.products import (
            DiagramCategory,
            is_limits_of_category,
        )

        assert first in self.ArrowCategory() and second in self.ArrowCategory()
        assert first.domain() is second.domain()
        assert first.codomain() is second.codomain()
        index = DiagramCategory(
            self,
            (first.domain(), first.codomain()),
            (first, second),
        )
        diagram = InclusionFunctor(index, self)
        result = self.LimitFunctor(index)(diagram)
        image = self.Limits(index)
        assert is_limits_of_category(image)
        assert image.contains_limit(result)
        return result

    def coequalizer(self, first: Arrow, second: Arrow) -> ColimitObject:
        """Return the chosen coequalizer of two parallel arrows."""
        from sage_categories.abstract_categories.functors import InclusionFunctor
        from sage_categories.abstract_categories.products import (
            DiagramCategory,
            is_colimits_of_category,
        )

        assert first in self.ArrowCategory() and second in self.ArrowCategory()
        assert first.domain() is second.domain()
        assert first.codomain() is second.codomain()
        index = DiagramCategory(
            self,
            (first.domain(), first.codomain()),
            (first, second),
        )
        diagram = InclusionFunctor(index, self)
        result = self.ColimitFunctor(index)(diagram)
        image = self.Colimits(index)
        assert is_colimits_of_category(image)
        assert image.contains_colimit(result)
        return result

    def pullback(self, first: Arrow, second: Arrow) -> LimitObject:
        """Return the chosen pullback of arrows with one codomain."""
        from sage_categories.abstract_categories.functors import InclusionFunctor
        from sage_categories.abstract_categories.products import (
            DiagramCategory,
            is_limits_of_category,
        )

        assert first in self.ArrowCategory() and second in self.ArrowCategory()
        assert first.codomain() is second.codomain()
        index = DiagramCategory(
            self,
            (first.domain(), second.domain(), first.codomain()),
            (first, second),
        )
        diagram = InclusionFunctor(index, self)
        result = self.LimitFunctor(index)(diagram)
        image = self.Limits(index)
        assert is_limits_of_category(image)
        assert image.contains_limit(result)
        return result

    def pushout(self, first: Arrow, second: Arrow) -> ColimitObject:
        """Return the chosen pushout of arrows with one domain."""
        from sage_categories.abstract_categories.functors import InclusionFunctor
        from sage_categories.abstract_categories.products import (
            DiagramCategory,
            is_colimits_of_category,
        )

        assert first in self.ArrowCategory() and second in self.ArrowCategory()
        assert first.domain() is second.domain()
        index = DiagramCategory(
            self,
            (first.domain(), first.codomain(), second.codomain()),
            (first, second),
        )
        diagram = InclusionFunctor(index, self)
        result = self.ColimitFunctor(index)(diagram)
        image = self.Colimits(index)
        assert is_colimits_of_category(image)
        assert image.contains_colimit(result)
        return result

    def Biproducts(self, diagram: Functor) -> Category:
        """Return chosen biproduct presentations for ``diagram``."""
        from sage_categories.abstract_categories.products import Biproducts

        assert diagram.codomain() is self
        return Biproducts(diagram)

    def OppositeCategory(self) -> Category:
        """Return the opposite category."""
        from sage_categories.abstract_categories.category_constructions import (
            OppositeCategory,
        )

        if self._opposite_category is None:
            self._opposite_category = OppositeCategory(self)
        return self._opposite_category

    def ProductCategory(self, second: Category) -> Category:
        """Return the binary product category."""
        from sage_categories.abstract_categories.category_constructions import (
            ProductCategory,
        )

        key = id(second)
        cached = self._product_categories.get(key)
        if cached is None:
            cached = ProductCategory(self, second)
            self._product_categories[key] = cached
        return cached

    def SliceOver(self, value: MathematicalObject) -> SliceOverCategory:
        """Return the slice category over ``value``."""
        from sage_categories.abstract_categories.slice_categories import SliceOver

        key = id(value)
        cached = self._slice_over_categories.get(key)
        if cached is None:
            cached = SliceOver(self, value)
            self._slice_over_categories[key] = cached
        return cached

    def CosliceUnder(self, value: MathematicalObject) -> CosliceUnderCategory:
        """Return the coslice category under ``value``."""
        from sage_categories.abstract_categories.slice_categories import CosliceUnder

        key = id(value)
        cached = self._coslice_under_categories.get(key)
        if cached is None:
            cached = CosliceUnder(self, value)
            self._coslice_under_categories[key] = cached
        return cached

    def Subobjects(self, value: MathematicalObject) -> SubobjectCategory:
        """Return the category of subobjects of ``value``."""
        from sage_categories.abstract_categories.slice_categories import Subobjects

        key = id(value)
        cached = self._subobject_categories.get(key)
        if cached is None:
            cached = Subobjects(self, value)
            self._subobject_categories[key] = cached
        return cached

    def Superobjects(self, value: MathematicalObject) -> SuperobjectCategory:
        """Return the category of superobjects of ``value``."""
        from sage_categories.abstract_categories.slice_categories import Superobjects

        key = id(value)
        cached = self._superobject_categories.get(key)
        if cached is None:
            cached = Superobjects(self, value)
            self._superobject_categories[key] = cached
        return cached

    def CoveringObjects(self, value: MathematicalObject) -> CoveringObjectCategory:
        """Return the category of epimorphisms into ``value``."""
        from sage_categories.abstract_categories.slice_categories import CoveringObjects

        key = id(value)
        cached = self._covering_object_categories.get(key)
        if cached is None:
            cached = CoveringObjects(self, value)
            self._covering_object_categories[key] = cached
        return cached

    def CoveredObjects(self, value: MathematicalObject) -> CoveredObjectCategory:
        """Return the category of epimorphisms from ``value``."""
        from sage_categories.abstract_categories.slice_categories import CoveredObjects

        key = id(value)
        cached = self._covered_object_categories.get(key)
        if cached is None:
            cached = CoveredObjects(self, value)
            self._covered_object_categories[key] = cached
        return cached

    def declared_methods(self) -> Mapping[str, DeclaredMethod]:
        """Return the compiled object-method catalogue."""
        return category_compiler().object_method_catalogue(self)

    def __repr__(self) -> str:
        return self.__class__.__name__
