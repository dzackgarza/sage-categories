from dataclasses import dataclass
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.native import NativeMorphismRealization as NativeMorphismRealization, NativeMorphismRealizations as NativeMorphismRealizations, NativeObjectRealization as NativeObjectRealization, NativeObjectRealizations as NativeObjectRealizations
from sage_categories.engines.julia_bridge import OscarHandle as OscarHandle
from sage_categories.kernel.refinement import refine as refine
from sage_categories.kernel.type_aliases import EqualityInput as EqualityInput

@dataclass(frozen=True, eq=False, slots=True)
class OscarRingConstruction:
    data: object

def retain_oscar_native_object(value: CategoryOfCategories.ElementType, native: object, construction: object) -> NativeObjectRealization[object, OscarRingConstruction]:
    ...

def oscar_native_object(value: CategoryOfCategories.ElementType) -> NativeObjectRealization[object, OscarRingConstruction]:
    ...

def retain_oscar_native_morphism(value: MorphismCategory.ObjectType, native: object) -> NativeMorphismRealization[object]:
    ...

def oscar_native_morphism(value: MorphismCategory.ObjectType) -> NativeMorphismRealization[object]:
    ...

def oscar_object_handle(value: CategoryOfCategories.ElementType) -> OscarHandle:
    ...

def oscar_element_handle(value: CategoryOfCategories.ElementType) -> OscarHandle:
    ...

def oscar_morphism_handle(value: MorphismCategory.ObjectType) -> OscarHandle:
    ...

def reconstruct_oscar_element(ring: CategoryOfCategories.ElementType, native: OscarHandle) -> CategoryOfCategories.ElementType:
    ...

def reconstruct_oscar_object(native: OscarHandle, construction: object) -> CategoryOfCategories.ElementType:
    ...

def reconstruct_oscar_morphism(source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, native: OscarHandle) -> MorphismCategory.ObjectType:
    ...
