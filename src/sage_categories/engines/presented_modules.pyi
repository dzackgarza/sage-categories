from sage_categories.algebra._presented_modules_cap import (
    presented_native_morphism as presented_native_morphism,
)
from sage_categories.algebra._presented_modules_cap import (
    presented_native_object as presented_native_object,
)
from sage_categories.algebra._presented_modules_cap import (
    retain_presented_native_morphism as retain_presented_native_morphism,
)
from sage_categories.algebra._presented_modules_cap import (
    retain_presented_native_object as retain_presented_native_object,
)
from sage_categories.engines.gap import PRESENTED_MODULE_PACKAGES as PRESENTED_MODULE_PACKAGES
from sage_categories.engines.gap import load_packages as load_packages

__all__ = [
    "coequalizer_mediator",
    "coequalizer_projection",
    "colift_along_epimorphism",
    "direct_sum_coproduct_lift",
    "direct_sum_product_lift",
    "retain_binary_biproduct",
    "tensor_element",
    "tensor_mediator",
    "tensor_morphism",
    "tensor_object",
    "zero_morphism",
]

def coequalizer_projection(first: object, second: object): ...
def coequalizer_mediator(projection: object, coequalizing: object): ...
def colift_along_epimorphism(epimorphism: object, morphism: object): ...
def retain_binary_biproduct(first: object, second: object, apex: object): ...
def direct_sum_product_lift(factors: tuple[object, ...], apex: object, source: object, components: tuple[object, ...]): ...
def direct_sum_coproduct_lift(factors: tuple[object, ...], apex: object, target: object, components: tuple[object, ...]): ...
def zero_morphism(source: object, target: object): ...
def tensor_object(first: object, second: object): ...
def tensor_element(first: object, second: object, tensor: object, left: object, right: object): ...
def tensor_mediator(first: object, second: object, tensor: object, target: object, biadditive): ...
def tensor_morphism(first: object, second: object, source_tensor: object, target_tensor: object): ...
