from dataclasses import dataclass
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.native import NativeMorphismRealizations as NativeMorphismRealizations, NativeObjectRealizations as NativeObjectRealizations

@dataclass(frozen=True, eq=False, slots=True)
class PresentedModuleConstruction:
    data: object

def has_presented_native_object(value: CategoryOfCategories.ElementType) -> bool:
    ...

def has_presented_native_morphism(value: MorphismCategory.ObjectType) -> bool:
    ...

def retain_presented_native_object(value: CategoryOfCategories.ElementType, native: object, construction: object):
    ...

def presented_native_object(value: CategoryOfCategories.ElementType):
    ...

def retain_presented_native_morphism(value: MorphismCategory.ObjectType, native: object):
    ...

def presented_native_morphism(value: MorphismCategory.ObjectType):
    ...
