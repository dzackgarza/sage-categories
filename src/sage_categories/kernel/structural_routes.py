"""Composable routes in the selected ordinary-functor graph."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import Functor
    from sage_categories.category import Category
    from sage_categories.types import Arrow, MathematicalObject


@dataclass(frozen=True)
class StructuralRoute:
    """A composable path of selected ordinary functors.

    The route records no new mathematical structure.  Its factors are the exact
    functor objects selected by category declarations, and application delegates to
    their declared object and morphism maps.
    """

    source: Category
    factors: tuple[Functor, ...]

    def __post_init__(self) -> None:
        if not self.factors:
            return
        assert self.factors[0].domain() is self.source
        assert all(
            first.codomain() is second.domain()
            for first, second in pairwise(self.factors)
        )

    def target(self) -> Category:
        """Return the route codomain."""
        if not self.factors:
            return self.source
        return self.factors[-1].codomain()

    def then(self, functor: Functor) -> StructuralRoute:
        """Append one composable selected functor."""
        assert self.target() is functor.domain()
        return StructuralRoute(self.source, (*self.factors, functor))

    def on_object(self, value: MathematicalObject) -> MathematicalObject:
        """Apply the exact object maps in order."""
        assert value in self.source
        image = value
        for functor in self.factors:
            image = functor.on_object(image)
        assert image in self.target()
        return image

    def on_morphism(self, arrow: Arrow) -> Arrow:
        """Apply the exact morphism maps in order."""
        assert self.source.contains_arrow(arrow)
        image = arrow
        for functor in self.factors:
            image = functor.on_morphism(image)
        assert self.target().contains_arrow(image)
        return image
