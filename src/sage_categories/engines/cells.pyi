import sage_categories_homotopy as homotopy
from dataclasses import dataclass, field
from sage_categories.cat.category import Category
from sage_categories.cat.morphisms import MorphismCategory
from typing import Literal
__all__ = ['native_signature', 'native_object', 'retain_identity', 'retain_composite', 'retain_whisker_left', 'retain_whisker_right', 'retain_generator', 'native_cell', 'retain_inverses', 'typecheck', 'dimension', 'boundary']

@dataclass(slots=True)
class _CellState:
    owner: Category
    signature: homotopy.Signature
    objects: dict[int, tuple[object, homotopy.Cell]] = field(default_factory=dict)
    morphisms: dict[int, tuple[object, homotopy.Cell]] = field(default_factory=dict)

def native_signature(owner: Category) -> homotopy.Signature:
    ...

def native_object(owner: Category, value: object) -> homotopy.Cell:
    ...

def retain_identity(owner: Category, value: MorphismCategory.ObjectType) -> homotopy.Cell:
    ...

def retain_composite(owner: Category, value: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> homotopy.Cell:
    ...

def retain_whisker_left(owner: Category, value: MorphismCategory.ObjectType, functor: MorphismCategory.ObjectType, transformation: MorphismCategory.ObjectType) -> homotopy.Cell:
    ...

def retain_whisker_right(owner: Category, value: MorphismCategory.ObjectType, transformation: MorphismCategory.ObjectType, functor: MorphismCategory.ObjectType) -> homotopy.Cell:
    ...

def retain_generator(owner: Category, value: MorphismCategory.ObjectType, *, invertibility: Literal['directed', 'invertible']='directed') -> homotopy.Cell:
    ...

def native_cell(owner: Category, value: MorphismCategory.ObjectType) -> homotopy.Cell:
    ...

def retain_inverses(owner: Category, forward: MorphismCategory.ObjectType, backward: MorphismCategory.ObjectType) -> None:
    ...

def typecheck(owner: Category, value: MorphismCategory.ObjectType) -> None:
    ...

def dimension(owner: Category, value: MorphismCategory.ObjectType) -> int:
    ...

def boundary(owner: Category, value: MorphismCategory.ObjectType, side: Literal['source', 'target'], depth: int=0) -> object:
    ...
