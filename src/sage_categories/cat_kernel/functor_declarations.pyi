from sage_categories.cat.functors import Functor as Functor
from sage_categories.kernel.refinement import install_functor_declaration_readers as install_functor_declaration_readers

def traces_placement(functor: Functor) -> bool:
    ...

def traces_inheritance(functor: Functor) -> bool:
    ...

def declares_point(functor: Functor) -> bool:
    ...

def install() -> None:
    ...
