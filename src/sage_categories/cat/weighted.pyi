from collections.abc import Callable

import sage_categories.cat.category
import sage_categories.cat.comma
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.comma import CommaSpecialization as CommaSpecialization
from sage_categories.cat.cones import cocone as cocone
from sage_categories.cat.cones import cocones as cocones
from sage_categories.cat.cones import cone as cone
from sage_categories.cat.cones import cones as cones
from sage_categories.cat.constructions import (
    UniversalPresentation as UniversalPresentation,
)
from sage_categories.cat.constructions import constructed_data as constructed_data
from sage_categories.cat.functors import Cat as Cat
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.indexed import Grothendieck as Grothendieck
from sage_categories.cat.indexed import IndexedCategories as IndexedCategories
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.opposites import OppositeCategory as OppositeCategory
from sage_categories.cat.opposites import opposite_morphism as opposite_morphism
from sage_categories.cat.predicates import Unknown as Unknown
from sage_categories.cat.shapes import discrete_functor as discrete_functor
from sage_categories.kernel.refinement import refine as refine
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function

__all__ = [
    "Elements",
    "Representations",
    "RepresentationsCategory",
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
    "restricted_yoneda",
    "separating_evaluation",
    "separating_evaluation_injection",
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

class _StaticRoles_RepresentationsCategory(sage_categories.cat.comma._StaticRoles_CommaSpecialization):
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def representing_object(self) -> CategoryOfCategories.ElementType: ...
        def representation_isomorphism(self) -> MorphismCategory.ObjectType: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def representing_morphism(self) -> MorphismCategory.ObjectType: ...
        def domain(self) -> RepresentationsCategory.ObjectType: ...
        def codomain(self) -> RepresentationsCategory.ObjectType: ...

class RepresentationsCategory(
    _StaticRoles_RepresentationsCategory,
    CommaSpecialization[_StaticRoles_RepresentationsCategory.ObjectType, _StaticRoles_RepresentationsCategory.ElementType, _StaticRoles_RepresentationsCategory.MorphismType],
):
    def __init__(self, represented: Functor, embedding: Functor) -> None: ...
    def represented_functor(self) -> Functor: ...
    def yoneda_embedding(self) -> Functor: ...
    def __call__(self, representing_object: CategoryOfCategories.ElementType, isomorphism: MorphismCategory.ObjectType) -> RepresentationsCategory.ObjectType: ...
    def from_arrow(
        self, first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType, arrow: MorphismCategory.ObjectType
    ) -> RepresentationsCategory.ObjectType: ...
    def construct_morphism(
        self, source: RepresentationsCategory.ObjectType, target: RepresentationsCategory.ObjectType, arrow: MorphismCategory.ObjectType
    ) -> RepresentationsCategory.MorphismType: ...

def Representations(functor: Functor) -> RepresentationsCategory: ...
def coyoneda(category: Category, sets: Category) -> Functor: ...
def restricted_yoneda(test: Functor, hom: Functor) -> Functor: ...
def separating_evaluation(test: Functor, hom: Functor) -> NaturalTransformation: ...
def separating_evaluation_injection(
    test: Functor, hom: Functor, value: CategoryOfCategories.ElementType, probe_point: CategoryOfCategories.ElementType, hom_point: CategoryOfCategories.ElementType
) -> MorphismCategory.ObjectType: ...
def coend_weight(hom: Functor) -> Functor: ...
def end(diagram: Functor, hom: Functor) -> CategoryOfCategories.ElementType: ...
def coend(diagram: Functor, hom: Functor) -> CategoryOfCategories.ElementType: ...
def natural_transformation_diagram(first: Functor, second: Functor, hom: Functor) -> Functor: ...
def natural_transformation_to_end(transformation: NaturalTransformation, source_hom: Functor, target_hom: Functor) -> CategoryOfCategories.ElementType: ...
def end_to_natural_transformation(
    point: CategoryOfCategories.ElementType, first: Functor, second: Functor, source_hom: Functor, target_hom: Functor
) -> NaturalTransformation: ...
