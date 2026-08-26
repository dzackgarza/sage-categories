"""Property subcategories of fixed-endpoint functor categories."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from sage_categories.abstract_categories.full_subcategories import FullSubcategory
from sage_categories.types import Decision, MathematicalObject, UNKNOWN

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functor_core import Functor, FunctorCategory
    from sage_categories.category import Category


class FunctorPropertySubcategory(FullSubcategory):
    """One proposition-defined property of functors with fixed endpoints."""

    def __init__(
        self,
        ambient_category: FunctorCategory,
        *,
        name: str,
        predicate_name: str,
        implications: Callable[[], tuple[Category, ...]],
    ) -> None:
        self._functor_ambient = ambient_category
        self._implications = implications
        self._implication_inclusions: dict[int, Functor] = {}

        def undecided(candidate: MathematicalObject) -> Decision:
            assert candidate in ambient_category
            return UNKNOWN

        undecided.__name__ = predicate_name
        super().__init__(ambient_category, undecided, name=name)

    def functor_category(self) -> FunctorCategory:
        return self._functor_ambient

    def property_inclusion(self) -> Functor:
        """Return this full property's categorical inclusion into its ambient."""
        return FullSubcategory.inclusion(self)

    def structure_functors(self) -> tuple[Functor, ...]:
        from sage_categories.abstract_categories.functor_core import InclusionFunctor

        implications = self._implications()
        if not implications:
            return (self.property_inclusion(),)
        selected: list[Functor] = []
        for target in implications:
            key = id(target)
            inclusion = self._implication_inclusions.get(key)
            if inclusion is None:
                inclusion = InclusionFunctor(self, target)
                self._implication_inclusions[key] = inclusion
            selected.append(inclusion)
        return tuple(selected)

    def __call__(self, candidate: Functor) -> Functor:
        refined = super().__call__(candidate)
        return refined

    def inclusion(self) -> Functor:
        """Construct the asserted inclusion functor between the endpoints."""
        from sage_categories.abstract_categories.functor_core import InclusionFunctor

        ambient = self.functor_category()
        return self(InclusionFunctor(ambient.domain(), ambient.codomain()))

    def identity(self) -> Functor:
        """Construct the identity functor in this trusted property category."""
        from sage_categories.abstract_categories.functor_core import IdentityFunctor

        ambient = self.functor_category()
        assert ambient.domain() is ambient.codomain()
        return self(IdentityFunctor(ambient.domain(), hom_category=ambient))
