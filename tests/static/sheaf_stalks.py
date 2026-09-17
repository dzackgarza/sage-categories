"""Static projection for represented sheaf stalks and germs."""

from typing import assert_type

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.geometry.ringed_spaces import RingedSpacesCategory
from sage_categories.geometry.sheaves import RingSheaf
from sage_categories.geometry.stalks import (
    ring_stalk,
    ringed_stalk_map,
    stalk_diagram,
    stalk_germ,
    stalk_presentation,
)


def stalk_types(
    sheaf: RingSheaf[frozenset[int]],
    point: CategoryOfCategories.ElementType,
    open_key: frozenset[int],
    mapping: RingedSpacesCategory.MorphismType,
) -> None:
    assert_type(ring_stalk(sheaf, point), CategoryOfCategories.ElementType)
    assert_type(stalk_diagram(sheaf, point), Functor)
    assert_type(stalk_presentation(sheaf, point), LimitConesCategory.ObjectType)
    assert_type(stalk_germ(sheaf, point, open_key), MorphismCategory.ObjectType)
    assert_type(ringed_stalk_map(mapping, point), MorphismCategory.ObjectType)
