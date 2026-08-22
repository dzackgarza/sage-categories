"""Categories as objects of ``Cat``.

This is the runtime-independent form of the architecture in
``abstract_categories/cat.sage`` from the research preamble.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

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
        self._slice_over_categories: dict[int, Category] = {}
        self._coslice_under_categories: dict[int, Category] = {}
        self._subobject_categories: dict[int, Category] = {}
        self._superobject_categories: dict[int, Category] = {}
        self._covering_object_categories: dict[int, Category] = {}
        self._covered_object_categories: dict[int, Category] = {}
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
        codomain: MathematicalObject,
    ) -> HomCategoryObject:
        """Return ``Hom_C(domain, codomain)``."""
        assert domain in self and codomain in self
        return self.HomCategory().Of(domain, codomain)

    def End(self, value: MathematicalObject) -> HomCategoryObject:
        """Return ``End_C(value)``."""
        assert value in self
        return self.EndCategory().Of(value, value)

    def Mono(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> HomCategoryObject:
        """Return the monomorphisms from domain to codomain."""
        return self.MonoCategory().Of(domain, codomain)

    def Epi(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> HomCategoryObject:
        """Return the epimorphisms from domain to codomain."""
        return self.EpiCategory().Of(domain, codomain)

    def Iso(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> HomCategoryObject:
        """Return the isomorphisms from domain to codomain."""
        return self.IsoCategory().Of(domain, codomain)

    def Aut(self, value: MathematicalObject) -> HomCategoryObject:
        """Return the automorphisms of ``value``."""
        return self.AutCategory().Of(value, value)

    def identity(self, value: MathematicalObject) -> Arrow:
        """Return the identity arrow of ``value``."""
        return self.Hom(value, value).identity()

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
        from sage_categories.abstract_categories.arrow_categories import Core

        return Core(self)

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

    def Products(self, diagram: Functor) -> Category:
        """Return chosen product presentations for ``diagram``."""
        from sage_categories.abstract_categories.products import Products

        assert diagram.codomain() is self
        return Products(diagram)

    def Coproducts(self, diagram: Functor) -> Category:
        """Return chosen coproduct presentations for ``diagram``."""
        from sage_categories.abstract_categories.products import Coproducts

        assert diagram.codomain() is self
        return Coproducts(diagram)

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

    def SliceOver(self, value: MathematicalObject) -> Category:
        """Return the slice category over ``value``."""
        from sage_categories.abstract_categories.slice_categories import SliceOver

        key = id(value)
        cached = self._slice_over_categories.get(key)
        if cached is None:
            cached = SliceOver(self, value)
            self._slice_over_categories[key] = cached
        return cached

    def CosliceUnder(self, value: MathematicalObject) -> Category:
        """Return the coslice category under ``value``."""
        from sage_categories.abstract_categories.slice_categories import CosliceUnder

        key = id(value)
        cached = self._coslice_under_categories.get(key)
        if cached is None:
            cached = CosliceUnder(self, value)
            self._coslice_under_categories[key] = cached
        return cached

    def Subobjects(self, value: MathematicalObject) -> Category:
        """Return the category of subobjects of ``value``."""
        from sage_categories.abstract_categories.slice_categories import Subobjects

        key = id(value)
        cached = self._subobject_categories.get(key)
        if cached is None:
            cached = Subobjects(self, value)
            self._subobject_categories[key] = cached
        return cached

    def Superobjects(self, value: MathematicalObject) -> Category:
        """Return the category of superobjects of ``value``."""
        from sage_categories.abstract_categories.slice_categories import Superobjects

        key = id(value)
        cached = self._superobject_categories.get(key)
        if cached is None:
            cached = Superobjects(self, value)
            self._superobject_categories[key] = cached
        return cached

    def CoveringObjects(self, value: MathematicalObject) -> Category:
        """Return the category of epimorphisms into ``value``."""
        from sage_categories.abstract_categories.slice_categories import CoveringObjects

        key = id(value)
        cached = self._covering_object_categories.get(key)
        if cached is None:
            cached = CoveringObjects(self, value)
            self._covering_object_categories[key] = cached
        return cached

    def CoveredObjects(self, value: MathematicalObject) -> Category:
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
