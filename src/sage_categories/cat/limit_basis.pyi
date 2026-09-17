from collections.abc import Callable
from dataclasses import dataclass
from sage_categories.cat.canonical import FinitePresentedCategory as FinitePresentedCategory
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.cones import ConeCategory as ConeCategory, LimitConesCategory as LimitConesCategory, cone as cone, cones as cones, limit_cones as limit_cones
from sage_categories.cat.constructions import constructed_data as constructed_data
from sage_categories.cat.diagrams import from_object_rule as from_object_rule
from sage_categories.cat.functors import Cat as Cat, Fun as Fun, Functor as Functor, NaturalTransformation as NaturalTransformation
from sage_categories.cat.morphisms import Mor as Mor, MorphismCategory as MorphismCategory
from sage_categories.cat.opposites import OppositeCategory as OppositeCategory, opposite_morphism as opposite_morphism
from sage_categories.cat.predicates import Unknown as Unknown, ask as ask
from sage_categories.cat.shapes import Discrete as Discrete
from sage_categories.kernel.retention import identity_key as identity_key, identity_positions as identity_positions
from sage_categories.kernel.sage_runtime import cached_function as cached_function

@dataclass(frozen=True)
class DiagramPresentation:
    vertices: Functor
    source: Functor
    target: Functor
    arrows: NaturalTransformation

def diagram_presentation(shape: Category) -> DiagramPresentation:
    ...

def parallel_pair(first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> Functor:
    ...

def limit_from_products_equalizers(diagram: Functor) -> CategoryOfCategories.ElementType:
    ...

def colimit_from_coproducts_coequalizers(diagram: Functor) -> CategoryOfCategories.ElementType:
    ...
