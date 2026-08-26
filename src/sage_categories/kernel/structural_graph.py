"""Validation of the selected ordinary-functor inheritance graph."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import Functor
    from sage_categories.category import Category


def selected_structure_functors(
    category: Category,
) -> tuple[Functor, ...]:
    """Return and validate ``category``'s immediate selected functors.

    Selection is compiler input only.  Every selected value is an ordinary
    functor whose domain is the declaring category; endpoint pairs and object
    fields never synthesize an edge.
    """
    from sage_categories.abstract_categories.cat import Cat

    functors = category.structure_functors()
    assert isinstance(functors, tuple)
    assert all(functor in Cat().ArrowCategory() for functor in functors)
    assert all(functor.domain() is category for functor in functors)
    assert len({id(functor) for functor in functors}) == len(functors)
    return functors
