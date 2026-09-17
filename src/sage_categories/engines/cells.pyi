import sage_categories_homotopy as homotopy
from dataclasses import dataclass, field
from sage_categories.cat.category import Category as Category, composite_factors as composite_factors, is_composite as is_composite
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict, cached_function as cached_function
from typing import Literal

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
