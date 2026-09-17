from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.diagrams import cospan_diagram as cospan_diagram
from sage_categories.cat.functors import Functor as Functor

__all__ = ["base_change"]

def base_change(base_functor: Functor, defining_functor: Functor) -> Functor: ...
