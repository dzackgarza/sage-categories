"""Strict fibers of owned functors.

For ``p: E -> B`` and ``b in B``, the fiber is the strict pullback of ``p``
along the point functor ``b: * -> B``. Mathlib's
``CategoryTheory.Functor.Fiber`` uses objects ``a`` with ``p(a) = b`` and
morphisms ``f`` with ``p(f) = id_b``. Its ``fiberInclusion`` is the functor to
``E``. See
https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/FiberedCategory/Fiber.html
(inspected 2026-09-01).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.cat.cat_constructions import LimitSubcategory, limit_of_categories
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.functors import Cat, Functor
from sage_categories.kernel.sage_runtime import MonoDict

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

__all__ = ["FiberCategory", "fiber"]


class FiberCategory(LimitSubcategory):
    """The strict fiber of a functor over one object of its codomain."""

    def __init__(
        self,
        diagram: Functor,
        defining_functor: Functor,
        base_object: CategoryOfCategories.ElementType,
    ) -> None:
        self._defining_functor = defining_functor
        self._base_object = base_object
        super().__init__(diagram)

    def defining_functor(self) -> Functor:
        """Return ``p: E -> B`` whose fiber this category is."""
        return self._defining_functor

    def base_object(self) -> CategoryOfCategories.ElementType:
        """Return the object ``b`` over which this fiber lies."""
        return self._base_object

    def inclusion(self) -> Functor:
        """Return the retained pullback projection from this fiber to ``E``."""
        return Cat().Pullbacks().presentation(self).leg(0)

    def __repr__(self) -> str:
        return f"{self._defining_functor!r}.Fiber({self._base_object!r})"


_fibers: MonoDict = MonoDict()


def fiber(
    defining_functor: Functor,
    base_object: CategoryOfCategories.ElementType,
) -> FiberCategory:
    """Return the retained strict fiber of ``defining_functor`` over ``base_object``."""
    base = defining_functor.codomain()
    assert base_object in base, f"{base_object!r} is not an object of {base!r}"
    if defining_functor not in _fibers:
        _fibers[defining_functor] = MonoDict()
    retained = _fibers[defining_functor]
    if base_object not in retained:
        diagram = cospan_diagram(Cat(), defining_functor, base.point_functor(base_object))
        result = limit_of_categories(
            diagram,
            Cat().Pullbacks(),
            lambda defining_diagram: FiberCategory(
                defining_diagram,
                defining_functor,
                base_object,
            ),
        )
        assert isinstance(result, FiberCategory)
        result.inclusion()
        retained[base_object] = result
    return retained[base_object]
