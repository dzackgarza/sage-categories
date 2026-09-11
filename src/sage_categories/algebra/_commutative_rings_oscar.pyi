from dataclasses import dataclass

from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.native import (
    NativeMorphismRealization as NativeMorphismRealization,
)
from sage_categories.cat.native import (
    NativeMorphismRealizations as NativeMorphismRealizations,
)
from sage_categories.cat.native import (
    NativeObjectRealization as NativeObjectRealization,
)
from sage_categories.cat.native import (
    NativeObjectRealizations as NativeObjectRealizations,
)
from sage_categories.engines.julia_bridge import OscarHandle as OscarHandle

__all__ = [
    "OscarRingConstruction",
    "oscar_element_handle",
    "oscar_morphism_handle",
    "oscar_native_morphism",
    "oscar_native_object",
    "oscar_object_handle",
    "reconstruct_oscar_morphism",
    "reconstruct_oscar_object",
    "retain_oscar_native_morphism",
    "retain_oscar_native_object",
]

@dataclass(frozen=True, eq=False, slots=True)
class OscarRingConstruction:
    data: object

def retain_oscar_native_object(value: CategoryOfCategories.ElementType, native: object, construction: object) -> NativeObjectRealization[object, OscarRingConstruction]: ...
def oscar_native_object(value: CategoryOfCategories.ElementType) -> NativeObjectRealization[object, OscarRingConstruction]: ...
def retain_oscar_native_morphism(value: MorphismCategory.ObjectType, native: object) -> NativeMorphismRealization[object]: ...
def oscar_native_morphism(value: MorphismCategory.ObjectType) -> NativeMorphismRealization[object]: ...
def oscar_object_handle(value: CategoryOfCategories.ElementType) -> OscarHandle: ...
def oscar_element_handle(value: CategoryOfCategories.ElementType) -> OscarHandle: ...
def oscar_morphism_handle(value: MorphismCategory.ObjectType) -> OscarHandle: ...
def reconstruct_oscar_object(native: OscarHandle, construction: object) -> CategoryOfCategories.ElementType: ...
def reconstruct_oscar_morphism(source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, native: OscarHandle) -> MorphismCategory.ObjectType: ...
