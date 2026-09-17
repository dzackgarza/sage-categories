from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.comma import CommaCategory as CommaCategory
from sage_categories.cat.cones import cocone as cocone
from sage_categories.cat.cones import cocones as cocones
from sage_categories.cat.cones import cone as cone
from sage_categories.cat.cones import cones as cones
from sage_categories.cat.constructions import (
    UniversalPresentation as UniversalPresentation,
)
from sage_categories.cat.constructions import constructed_data as constructed_data
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.slices import comma_category as comma_category
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function

__all__ = ["left_kan_adjunction", "left_kan_desc", "left_kan_extension", "left_kan_unit", "right_kan_adjunction", "right_kan_counit", "right_kan_extension", "right_kan_lift"]

def left_kan_extension(along: Functor, functor: Functor) -> Functor: ...
def left_kan_unit(along: Functor, functor: Functor) -> NaturalTransformation: ...
def right_kan_extension(along: Functor, functor: Functor) -> Functor: ...
def right_kan_counit(along: Functor, functor: Functor) -> NaturalTransformation: ...
def right_kan_lift(along: Functor, functor: Functor, candidate: Functor, transformation: NaturalTransformation) -> NaturalTransformation: ...
def left_kan_desc(along: Functor, functor: Functor, candidate: Functor, transformation: NaturalTransformation) -> NaturalTransformation: ...
def right_kan_adjunction(along: Functor, values: Category) -> CategoryOfCategories.ElementType: ...
def left_kan_adjunction(along: Functor, values: Category) -> CategoryOfCategories.ElementType: ...
