"""Change of base through the generic pullback in ``Cat()``."""

from __future__ import annotations

from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.functors import Cat, Functor

__all__ = ["base_change"]


def base_change(base_functor: Functor, defining_functor: Functor) -> Functor:
    """Return ``D ×_C E -> D`` for ``D -> C <- E``.

    The pullback's retained limiting presentation owns both projections and the
    common composite to ``C``.
    """
    assert base_functor.codomain() is defining_functor.codomain(), (
        f"{base_functor!r} and {defining_functor!r} have different codomains"
    )
    diagram = cospan_diagram(Cat(), base_functor, defining_functor)
    pullbacks = Cat().Pullbacks()
    pullback = pullbacks(diagram)
    presentation = pullbacks.universal_data(diagram)
    projection = presentation.leg(0)
    assert projection.domain() is pullback
    return projection
