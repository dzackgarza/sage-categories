from dataclasses import dataclass

from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.native import NativeMorphismRealizations as NativeMorphismRealizations
from sage_categories.cat.native import NativeObjectRealizations as NativeObjectRealizations

__all__ = ["PresentedModuleConstruction", "presented_native_morphism", "presented_native_object", "retain_presented_native_morphism", "retain_presented_native_object"]

@dataclass(frozen=True, eq=False, slots=True)
class PresentedModuleConstruction:
    data: object

def retain_presented_native_object(value: CategoryOfCategories.ElementType, native: object, construction: object): ...
def presented_native_object(value: CategoryOfCategories.ElementType): ...
def retain_presented_native_morphism(value: MorphismCategory.ObjectType, native: object): ...
def presented_native_morphism(value: MorphismCategory.ObjectType): ...
