from dataclasses import dataclass
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import NativeMorphismRealization, NativeObjectRealization
__all__ = ['OscarRingConstruction', 'retain_oscar_native_object', 'oscar_native_object', 'retain_oscar_native_morphism', 'oscar_native_morphism', 'reconstruct_oscar_object', 'reconstruct_oscar_morphism']

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

def reconstruct_oscar_object(native: object, construction: object) -> CategoryOfCategories.ElementType:
    ...

def reconstruct_oscar_morphism(source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, native: object) -> MorphismCategory.ObjectType:
    ...
