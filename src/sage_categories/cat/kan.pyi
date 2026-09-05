from sage_categories.cat.functors import Functor, NaturalTransformation
__all__ = ['left_kan_extension', 'left_kan_unit', 'right_kan_extension', 'right_kan_counit', 'right_kan_lift', 'left_kan_desc']

def left_kan_extension(along: Functor, functor: Functor) -> Functor:
    ...

def left_kan_unit(along: Functor, functor: Functor) -> NaturalTransformation:
    ...

def right_kan_extension(along: Functor, functor: Functor) -> Functor:
    ...

def right_kan_counit(along: Functor, functor: Functor) -> NaturalTransformation:
    ...

def right_kan_lift(along: Functor, functor: Functor, candidate: Functor, transformation: NaturalTransformation) -> NaturalTransformation:
    ...

def left_kan_desc(along: Functor, functor: Functor, candidate: Functor, transformation: NaturalTransformation) -> NaturalTransformation:
    ...
