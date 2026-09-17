from sage_categories.cat.calculus import binary_product_data as binary_product_data
from sage_categories.cat.calculus import pair_maps as pair_maps
from sage_categories.cat.calculus import product_functor as product_functor
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.opposites import opposite_morphism as opposite_morphism
from sage_categories.cat.weighted import coend as coend
from sage_categories.cat.weighted import coend_weight as coend_weight
from sage_categories.cat.weighted import hom_functor as hom_functor
from sage_categories.cat.weighted import weighted_colimit_desc as weighted_colimit_desc
from sage_categories.cat.weighted import weighted_colimit_map as weighted_colimit_map
from sage_categories.cat.weighted import weighted_injection as weighted_injection
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function

__all__ = ["Profunctors", "compose_profunctor_transformations", "compose_profunctors", "identity_profunctor", "profunctor_unitor"]

def Profunctors(first: Category, second: Category, sets: Category) -> Category: ...
def compose_profunctors(first: Functor, second: Functor, hom: Functor) -> Functor: ...
def compose_profunctor_transformations(first: NaturalTransformation, second: NaturalTransformation, hom: Functor) -> NaturalTransformation: ...
def identity_profunctor(category: Category, sets: Category) -> Functor: ...
def profunctor_unitor(profunctor: Functor, hom: Functor, left: bool = True) -> NaturalTransformation: ...
