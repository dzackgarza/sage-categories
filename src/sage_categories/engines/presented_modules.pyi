from collections.abc import Callable
from dataclasses import dataclass
from sage.libs.gap.element import GapElement
from sage_categories.algebra._presented_modules_cap import has_presented_native_morphism as has_presented_native_morphism, has_presented_native_object as has_presented_native_object, presented_native_morphism as presented_native_morphism, presented_native_object as presented_native_object, retain_presented_native_morphism as retain_presented_native_morphism, retain_presented_native_object as retain_presented_native_object
from sage_categories.engines.gap import PRESENTED_MODULE_PACKAGES as PRESENTED_MODULE_PACKAGES, load_packages as load_packages

@dataclass(frozen=True, eq=False, slots=True)
class KernelPresentation:
    parser: Callable[[str], object]
    ring: GapElement
    category: GapElement
    source: GapElement
    target: GapElement
    morphism: GapElement
    embedding: GapElement

    def relation_rows(self):
        ...

    def inclusion_rows(self):
        ...

    def lift_row(self, source_row):
        ...

def kernel_presentation(*, variable_names: tuple[str, ...], owned_ring: Callable[[str], object], source_rank: int, target_rank: int, source_relation_rows, target_relation_rows, morphism_rows) -> KernelPresentation:
    ...

def equal_morphisms(first: object, second: object) -> bool:
    ...

def coequalizer_projection(first: object, second: object):
    ...

def coequalizer_mediator(projection: object, coequalizing: object, first: object, second: object):
    ...

def colift_along_epimorphism(epimorphism: object, morphism: object):
    ...

def retain_binary_biproduct(first: object, second: object, apex: object):
    ...

def direct_sum_product_lift(factors: tuple[object, ...], apex: object, source: object, components: tuple[object, ...]):
    ...

def direct_sum_coproduct_lift(factors: tuple[object, ...], apex: object, target: object, components: tuple[object, ...]):
    ...

def zero_morphism(source: object, target: object):
    ...

def tensor_object(first: object, second: object):
    ...

def tensor_element(first: object, second: object, tensor: object, left: object, right: object):
    ...

def tensor_mediator(first: object, second: object, tensor: object, target: object, biadditive):
    ...

def tensor_morphism(first: object, second: object, source_tensor: object, target_tensor: object):
    ...

def tensor_associator(first: object, second: object, third: object, source_tensor: object, target_tensor: object, *, left_to_right: bool):
    ...

def tensor_left_unitor(group: object, tensor: object, *, inverse: bool):
    ...

def tensor_right_unitor(group: object, tensor: object, *, inverse: bool):
    ...
