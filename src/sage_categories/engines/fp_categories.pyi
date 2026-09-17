from dataclasses import dataclass
from sage.libs.gap.element import GapElement
from sage_categories.engines.gap import FINITE_CATEGORY_PACKAGES as FINITE_CATEGORY_PACKAGES, load_packages as load_packages
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function

def reduce_word(category: object, source: object, target: object, word: tuple[str, ...]) -> tuple[str, ...]:
    ...

def compose_morphisms(category: object, second: object, first: object) -> object:
    ...

def inverse_morphism(category: object, morphism: object) -> object:
    ...

def is_isomorphism(category: object, morphism: object) -> bool | None:
    ...

def finite_morphisms(category: object) -> tuple[tuple[int, int, tuple[str, ...]], ...] | None:
    ...

def native_category(category: object) -> GapElement:
    ...

def native_object(category: object, value: object) -> GapElement:
    ...

def native_morphism(category: object, value: object) -> GapElement:
    ...

def owned_object(category: object, native: GapElement) -> object:
    ...

def terminal_object(category: object) -> object | None:
    ...

def owned_morphism(category: object, native: GapElement) -> object:
    ...
