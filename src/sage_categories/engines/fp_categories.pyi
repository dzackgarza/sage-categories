from dataclasses import dataclass
from sage.libs.gap.element import GapElement
__all__ = ['reduce_word', 'finite_morphisms', 'native_category', 'native_object', 'native_morphism', 'owned_object', 'terminal_object', 'owned_morphism']

@dataclass(frozen=True, slots=True)
class _Presentation:
    owner: object
    native: GapElement
    ambient: GapElement
    ambient_objects: tuple[GapElement, ...]
    native_objects: tuple[GapElement, ...]
    generator_names: tuple[str, ...]
    generator_indices: dict[str, int]
    quotient: bool

def reduce_word(category: object, source: object, target: object, word: tuple[str, ...]) -> tuple[str, ...]:
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
