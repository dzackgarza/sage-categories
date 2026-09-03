from sage_categories.cat.functors import Functor
__all__ = ['traces_placement', 'traces_inheritance', 'declares_point', 'install']

def traces_placement(functor: Functor) -> bool:
    ...

def traces_inheritance(functor: Functor) -> bool:
    ...

def declares_point(functor: Functor) -> bool:
    ...

def install() -> None:
    ...
