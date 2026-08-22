"""Runtime values used by the owned categorical foundation.

The mathematical organization follows the abstract-category layer in
``dzack_research.preamble.categories.abstract_categories``. The runtime is
independent of Sage's category classes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import StructuralFunctor
    from sage_categories.abstract_categories.hom_categories import HomCategory
    from sage_categories.category import Category

type MembershipInput = Any


_VALUES: dict[int, MathematicalObject] = {}


def registered_value(candidate: MembershipInput) -> MathematicalObject | None:
    """Return the owned mathematical value represented by ``candidate``."""
    candidate_id = id(candidate)
    value = _VALUES.get(candidate_id)
    if value is not None and id(value) == candidate_id:
        return value
    return None


class MathematicalObject:
    """An object of a category, with cached structural-functor images."""

    def __init__(self, *, category: Category | None) -> None:
        self._category = category
        self._structural_images: dict[int, MathematicalObject] = {}
        if category is not None:
            self._structural_images[id(category)] = self
        _VALUES[id(self)] = self

    def category(self) -> Category:
        """Return the category in which this object was constructed."""
        assert self._category is not None
        return self._category

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> HomCategory:
        """Return the hom category from this object to ``target``."""
        target = domain
        if codomain is None:
            from sage_categories.abstract_categories.arrow_categories import (
                common_category,
            )

            category = common_category((self, target))
        else:
            from sage_categories.abstract_categories.cat import Cat

            assert Cat().contains_category(codomain)
            category = codomain
        return category.Hom(self, target)

    def End(self, value: MathematicalObject | None = None) -> HomCategory:
        """Return the endomorphism category of this object."""
        assert value is None
        return self.category().End(self)

    def Aut(self, value: MathematicalObject | None = None) -> HomCategory:
        """Return the automorphism category of this object."""
        assert value is None
        return self.category().Aut(self)

    def Iso(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> HomCategory:
        """Return the isomorphisms from this object to ``target``."""
        from sage_categories.abstract_categories.arrow_categories import (
            common_category,
        )

        assert codomain is None
        target = domain
        return common_category((self, target)).Iso(self, target)

    def Mono(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> HomCategory:
        """Return the monomorphisms from this object to ``target``."""
        from sage_categories.abstract_categories.arrow_categories import (
            common_category,
        )

        assert codomain is None
        target = domain
        return common_category((self, target)).Mono(self, target)

    def Epi(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> HomCategory:
        """Return the epimorphisms from this object to ``target``."""
        from sage_categories.abstract_categories.arrow_categories import (
            common_category,
        )

        assert codomain is None
        target = domain
        return common_category((self, target)).Epi(self, target)

    def identity(self, value: MathematicalObject | None = None) -> Arrow:
        """Return the identity arrow of this object."""
        assert value is None
        return self.category().identity(self)

    def subobjects(self) -> Category:
        """Return the category of monomorphisms into this object."""
        return self.category().Subobjects(self)

    def superobjects(self) -> Category:
        """Return the category of monomorphisms from this object."""
        return self.category().Superobjects(self)

    def covering_objects(self) -> Category:
        """Return the category of epimorphisms into this object."""
        return self.category().CoveringObjects(self)

    def covered_objects(self) -> Category:
        """Return the category of epimorphisms from this object."""
        return self.category().CoveredObjects(self)

    def _belongs_to(self, category: Category) -> bool:
        if self._category is None:
            return False
        return self._category is category or self._category.is_subcategory(category)

    def _belongs_to_hom(self, hom_category: HomCategory) -> bool:
        return False

    def _is_arrow_in(self, category: Category) -> bool:
        return False

    def _image_along(
        self,
        route: tuple[StructuralFunctor, ...],
    ) -> MathematicalObject:
        value = self
        for functor in route:
            codomain = functor.codomain()
            key = id(codomain)
            cached = self._structural_images.get(key)
            if cached is not None:
                value = cached
                continue
            value = functor.on_object(value)
            assert value in codomain
            self._structural_images[key] = value
        return value


class MathematicalElement(MathematicalObject):
    """An element of a mathematical object."""

    def __init__(self, *, category: Category) -> None:
        super().__init__(category=category)


class Arrow(MathematicalElement):
    """An object of ``Ar(C)`` and an element of one hom category of ``C``."""

    def __init__(self, *, hom_category: HomCategory) -> None:
        self._hom_category = hom_category
        super().__init__(
            category=hom_category.base_category().ArrowCategory(),
        )

    def hom_category(self) -> HomCategory:
        """Return the hom category containing this arrow."""
        return self._hom_category

    def base_category(self) -> Category:
        """Return the category in which this arrow has its endpoints."""
        return self._hom_category.base_category()

    def domain(self) -> MathematicalObject:
        """Return the source object."""
        return self._hom_category.domain()

    def codomain(self) -> MathematicalObject:
        """Return the target object."""
        return self._hom_category.codomain()

    def source(self) -> MathematicalObject:
        """Return the source object."""
        return self.domain()

    def target(self) -> MathematicalObject:
        """Return the target object."""
        return self.codomain()

    def forward(self) -> Arrow:
        """Return the represented ordinary arrow."""
        return self

    def _belongs_to_hom(self, hom_category: HomCategory) -> bool:
        own_hom_category = self._hom_category
        return own_hom_category is hom_category or (
            own_hom_category.domain() is hom_category.domain()
            and own_hom_category.codomain() is hom_category.codomain()
            and own_hom_category.hom_category().is_subcategory(hom_category.hom_category())
        )

    def _is_arrow_in(self, category: Category) -> bool:
        base = self.base_category()
        return base is category or base.is_subcategory(category)

    def __mul__(self, first: Arrow) -> Arrow:
        """Return this arrow after ``first``."""
        return self.base_category().compose(self, first)
