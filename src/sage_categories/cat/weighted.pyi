from collections.abc import Callable

from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.cones import cocone as cocone
from sage_categories.cat.cones import cocones as cocones
from sage_categories.cat.cones import cone as cone
from sage_categories.cat.cones import cones as cones
from sage_categories.cat.constructions import constructed_data as constructed_data
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.indexed import Grothendieck as Grothendieck
from sage_categories.cat.indexed import IndexedCategories as IndexedCategories
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.opposites import opposite_morphism as opposite_morphism
from sage_categories.cat.predicates import Unknown as Unknown
from sage_categories.cat.shapes import discrete_functor as discrete_functor
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function

__all__ = [
    "Elements",
    "coend",
    "coend_weight",
    "coyoneda",
    "element",
    "element_projection",
    "end",
    "end_to_natural_transformation",
    "hom_functor",
    "natural_transformation_diagram",
    "natural_transformation_to_end",
    "weighted_colimit",
    "weighted_colimit_desc",
    "weighted_colimit_map",
    "weighted_injection",
    "weighted_limit",
    "weighted_limit_lift",
    "weighted_limit_map",
    "weighted_projection",
    "yoneda",
]
type WeightedComponents = Callable[[CategoryOfCategories.ElementType, CategoryOfCategories.ElementType], MorphismCategory.ObjectType]

def element_projection(weight: Functor) -> Functor: ...
def Elements(weight: Functor) -> Category: ...
def element(weight: Functor, vertex: CategoryOfCategories.ElementType, point: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType: ...
def weighted_limit(weight: Functor, diagram: Functor) -> CategoryOfCategories.ElementType: ...
def weighted_colimit(weight: Functor, diagram: Functor) -> CategoryOfCategories.ElementType: ...
def weighted_projection(
    weight: Functor, diagram: Functor, vertex: CategoryOfCategories.ElementType, point: CategoryOfCategories.ElementType
) -> MorphismCategory.ObjectType: ...
def weighted_injection(weight: Functor, diagram: Functor, vertex: CategoryOfCategories.ElementType, point: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType: ...
def weighted_limit_lift(weight: Functor, diagram: Functor, apex: CategoryOfCategories.ElementType, components: WeightedComponents) -> MorphismCategory.ObjectType: ...
def weighted_colimit_desc(weight: Functor, diagram: Functor, apex: CategoryOfCategories.ElementType, components: WeightedComponents) -> MorphismCategory.ObjectType: ...
def weighted_limit_map(weight: Functor, transformation: NaturalTransformation) -> MorphismCategory.ObjectType: ...
def weighted_colimit_map(weight: Functor, transformation: NaturalTransformation) -> MorphismCategory.ObjectType: ...
def hom_functor(category: Category, sets: Category) -> Functor: ...
def yoneda(category: Category, sets: Category) -> Functor: ...
def coyoneda(category: Category, sets: Category) -> Functor: ...
def coend_weight(hom: Functor) -> Functor: ...
def end(diagram: Functor, hom: Functor) -> CategoryOfCategories.ElementType: ...
def coend(diagram: Functor, hom: Functor) -> CategoryOfCategories.ElementType: ...
def natural_transformation_diagram(first: Functor, second: Functor, hom: Functor) -> Functor: ...
def natural_transformation_to_end(transformation: NaturalTransformation, source_hom: Functor, target_hom: Functor) -> CategoryOfCategories.ElementType: ...
def end_to_natural_transformation(
    point: CategoryOfCategories.ElementType, first: Functor, second: Functor, source_hom: Functor, target_hom: Functor
) -> NaturalTransformation: ...
