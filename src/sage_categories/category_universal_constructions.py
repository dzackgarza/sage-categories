"""Universal constructions formed from small diagram shapes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.abstract_categories.functors import InclusionFunctor
from sage_categories.abstract_categories.products import (
    DiagramCategory,
    is_colimits_of_category,
    is_limits_of_category,
)
from sage_categories.values import Arrow

if TYPE_CHECKING:
    from sage_categories.abstract_categories.products import ColimitObject, LimitObject
    from sage_categories.category import Category


def equalizer(category: Category, first: Arrow, second: Arrow) -> LimitObject:
    """Return the chosen equalizer of two parallel arrows."""
    assert first in category.ArrowCategory() and second in category.ArrowCategory()
    assert first.domain() is second.domain()
    assert first.codomain() is second.codomain()
    index = DiagramCategory(category, (first.domain(), first.codomain()), (first, second))
    diagram = InclusionFunctor(index, category)
    result = category.LimitFunctor(index)(diagram)
    image = category.Limits(index)
    assert is_limits_of_category(image)
    assert image.contains_limit(result)
    return result


def coequalizer(category: Category, first: Arrow, second: Arrow) -> ColimitObject:
    """Return the chosen coequalizer of two parallel arrows."""
    assert first in category.ArrowCategory() and second in category.ArrowCategory()
    assert first.domain() is second.domain()
    assert first.codomain() is second.codomain()
    index = DiagramCategory(category, (first.domain(), first.codomain()), (first, second))
    diagram = InclusionFunctor(index, category)
    result = category.ColimitFunctor(index)(diagram)
    image = category.Colimits(index)
    assert is_colimits_of_category(image)
    assert image.contains_colimit(result)
    return result


def pullback(category: Category, first: Arrow, second: Arrow) -> LimitObject:
    """Return the chosen pullback of arrows with one codomain."""
    assert first in category.ArrowCategory() and second in category.ArrowCategory()
    assert first.codomain() is second.codomain()
    index = DiagramCategory(category, (first.domain(), second.domain(), first.codomain()), (first, second))
    diagram = InclusionFunctor(index, category)
    result = category.LimitFunctor(index)(diagram)
    image = category.Limits(index)
    assert is_limits_of_category(image)
    assert image.contains_limit(result)
    return result


def pushout(category: Category, first: Arrow, second: Arrow) -> ColimitObject:
    """Return the chosen pushout of arrows with one domain."""
    assert first in category.ArrowCategory() and second in category.ArrowCategory()
    assert first.domain() is second.domain()
    index = DiagramCategory(category, (first.domain(), first.codomain(), second.codomain()), (first, second))
    diagram = InclusionFunctor(index, category)
    result = category.ColimitFunctor(index)(diagram)
    image = category.Colimits(index)
    assert is_colimits_of_category(image)
    assert image.contains_colimit(result)
    return result
