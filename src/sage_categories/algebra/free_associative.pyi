from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from sage_categories.cat.category import CategoryOfCategories
__all__ = ['IntegerFreeAssociativeConstruction', 'integer_free_associative_algebra', 'free_associative_underlying_module', 'free_associative_element', 'free_associative_generator', 'free_associative_coefficients', 'free_associative_product', 'free_associative_substitution', 'free_associative_underlying_morphism']
type Word = tuple[int, ...]

@dataclass(frozen=True, eq=False, slots=True)
class IntegerFreeAssociativeConstruction:
    names: tuple[str, ...]
    word_module: CategoryOfCategories.ElementType

def integer_free_associative_algebra(names: Sequence[str]=('x', 'y')):
    ...

def free_associative_underlying_module(algebra):
    ...

def free_associative_element(algebra, terms: Mapping[Word, int]):
    ...

def free_associative_generator(algebra, position: int):
    ...

def free_associative_coefficients(algebra, element) -> dict[Word, int]:
    ...

def free_associative_product(algebra, left, right):
    ...

def free_associative_substitution(algebra, images: Sequence[CategoryOfCategories.ElementType]):
    ...

def free_associative_underlying_morphism(algebra_morphism):
    ...
