from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor, NaturalTransformation
__all__ = ['Profunctors', 'compose_profunctors', 'compose_profunctor_transformations', 'identity_profunctor', 'profunctor_unitor']

def Profunctors(first: Category, second: Category, sets: Category) -> Category:
    ...

def compose_profunctors(first: Functor, second: Functor, hom: Functor) -> Functor:
    ...

def compose_profunctor_transformations(first: NaturalTransformation, second: NaturalTransformation, hom: Functor) -> NaturalTransformation:
    ...

def identity_profunctor(category: Category, sets: Category) -> Functor:
    ...

def profunctor_unitor(profunctor: Functor, hom: Functor, left: bool=True) -> NaturalTransformation:
    ...
