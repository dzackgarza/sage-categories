from dataclasses import dataclass
__all__ = ['coequalizer_projection', 'coequalizer_mediator', 'colift_along_epimorphism', 'retain_binary_biproduct', 'direct_sum_product_lift', 'direct_sum_coproduct_lift', 'zero_morphism', 'tensor_object', 'tensor_element', 'tensor_mediator', 'tensor_morphism']

@dataclass(frozen=True, eq=False, slots=True)
class _PresentationBridge:
    free: object
    engine: object

@dataclass(frozen=True, eq=False, slots=True)
class _DirectSumBridge:
    factors: tuple[object, ...]

def coequalizer_projection(first: object, second: object):
    ...

def coequalizer_mediator(projection: object, coequalizing: object):
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
