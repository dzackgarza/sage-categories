"""Same-object refinement preserves the exact static source type."""

from typing import assert_type

from sage_categories.cat.category import Category
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import ObjectOfCategory


class RefinableObject(ObjectOfCategory):
    def marker(self) -> int:
        return 1


def same_object(value: RefinableObject, target: Category) -> None:
    refined = refine(value, target)
    assert_type(refined, RefinableObject)
    assert_type(refined.marker(), int)
