"""Sentinel that fails when the Sage mypy profile loses exact category projection."""

from typing import assert_type

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.morphisms import FixedEndpointCategory, Mor, MorphismCategory
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import ObjectOfCategory


class ProbeObject(ObjectOfCategory):
    pass


class ProbeSource(CategoryOfCategories.ElementType):
    pass


class ProbeTarget(CategoryOfCategories.ElementType):
    pass


def mypy_runtime_probe(
    category: Category[[str], [int]],
    source: ProbeSource,
    target: ProbeTarget,
    value: ProbeObject,
) -> None:
    hom = Mor(category)(source, target)
    assert_type(hom, FixedEndpointCategory[[str], [int], ProbeSource, ProbeTarget])
    assert_type(Mor(category), MorphismCategory[[str], [int]])
    assert_type(refine(value, category), ProbeObject)
