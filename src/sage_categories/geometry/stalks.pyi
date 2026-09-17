from collections.abc import Hashable
from dataclasses import dataclass

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.geometry.ringed_spaces import RingedSpacesCategory
from sage_categories.geometry.sheaves import RingSheaf

__all__ = [
    "ring_stalk",
    "ringed_stalk_map",
    "stalk_diagram",
    "stalk_germ",
    "stalk_presentation",
]

@dataclass(frozen=True, eq=False, slots=True)
class _FiniteStalkData[PointDatum: Hashable]:
    sheaf: RingSheaf[frozenset[PointDatum]]
    point: CategoryOfCategories.ElementType
    neighborhoods: CategoryOfCategories.ElementType
    neighborhood_poset: CategoryOfCategories.ElementType
    inclusion: MorphismCategory.ObjectType
    neighborhood_category: Category
    diagram: Functor
    least_key: frozenset[PointDatum]
    least_vertex: CategoryOfCategories.ElementType

def ring_stalk[PointDatum: Hashable](
    sheaf: RingSheaf[frozenset[PointDatum]], point: CategoryOfCategories.ElementType
) -> CategoryOfCategories.ElementType: ...
def stalk_diagram[PointDatum: Hashable](
    sheaf: RingSheaf[frozenset[PointDatum]], point: CategoryOfCategories.ElementType
) -> Functor: ...
def stalk_presentation[PointDatum: Hashable](
    sheaf: RingSheaf[frozenset[PointDatum]], point: CategoryOfCategories.ElementType
) -> LimitConesCategory.ObjectType: ...
def stalk_germ[PointDatum: Hashable](
    sheaf: RingSheaf[frozenset[PointDatum]],
    point: CategoryOfCategories.ElementType,
    open_key: frozenset[PointDatum],
) -> MorphismCategory.ObjectType: ...
def ringed_stalk_map(
    mapping: RingedSpacesCategory.MorphismType,
    source_point: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType: ...
