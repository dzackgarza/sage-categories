from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import (
    NativeMorphismRealization,
    NativeObjectRealization,
)

class PresentedModuleConstruction:
    data: object

def retain_presented_native_object(value: CategoryOfCategories.ElementType, native: object, construction: object) -> NativeObjectRealization[object, PresentedModuleConstruction]: ...
def presented_native_object(value: CategoryOfCategories.ElementType) -> NativeObjectRealization[object, PresentedModuleConstruction]: ...
def retain_presented_native_morphism(value: MorphismCategory.ObjectType, native: object) -> NativeMorphismRealization[object]: ...
def presented_native_morphism(value: MorphismCategory.ObjectType) -> NativeMorphismRealization[object]: ...
