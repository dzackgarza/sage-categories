from dataclasses import dataclass
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import NativeMorphismRealization, NativeObjectRealization
from sage_categories.engines.julia_bridge import OscarHandle
__all__ = ['OscarRingConstruction', 'retain_oscar_native_object', 'oscar_native_object', 'retain_oscar_native_morphism', 'oscar_native_morphism', 'oscar_object_handle', 'oscar_element_handle', 'oscar_morphism_handle', 'reconstruct_oscar_object', 'reconstruct_oscar_morphism']

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

def reconstruct_oscar_object(native: OscarHandle, construction: object) -> CategoryOfCategories.ElementType:
    ...

def reconstruct_oscar_morphism(source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, native: OscarHandle) -> MorphismCategory.ObjectType:
    ...
