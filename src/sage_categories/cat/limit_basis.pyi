from dataclasses import dataclass

from sage_categories.cat.canonical import FinitePresentedCategory as FinitePresentedCategory
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.cones import ConeCategory as ConeCategory
from sage_categories.cat.cones import LimitConesCategory as LimitConesCategory
from sage_categories.cat.cones import cone as cone
from sage_categories.cat.cones import cones as cones
from sage_categories.cat.cones import limit_cones as limit_cones
from sage_categories.cat.constructions import constructed_data as constructed_data
from sage_categories.cat.diagrams import from_object_rule as from_object_rule
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.opposites import OppositeCategory as OppositeCategory
from sage_categories.cat.opposites import opposite_morphism as opposite_morphism
from sage_categories.cat.predicates import Unknown as Unknown
from sage_categories.cat.predicates import ask as ask
from sage_categories.cat.shapes import Discrete as Discrete
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function

__all__ = ["DiagramPresentation", "diagram_presentation", "parallel_pair", "limit_from_products_equalizers", "colimit_from_coproducts_coequalizers"]

@dataclass(frozen=True)
class DiagramPresentation:
    vertices: Functor
    source: Functor
    target: Functor
    arrows: NaturalTransformation

def diagram_presentation(shape: Category) -> DiagramPresentation: ...
def parallel_pair(first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> Functor: ...
def limit_from_products_equalizers(diagram: Functor) -> CategoryOfCategories.ElementType: ...
def colimit_from_coproducts_coequalizers(diagram: Functor) -> CategoryOfCategories.ElementType: ...
