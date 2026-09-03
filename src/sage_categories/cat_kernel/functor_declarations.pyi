from sage_categories.cat.functors import Functor
__all__ = ['traces_placement', 'traces_inheritance', 'install']

def traces_placement(functor: Functor) -> bool:
    ...

def traces_inheritance(functor: Functor) -> bool:
    ...

def install() -> None:
    ...
