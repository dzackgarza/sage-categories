from collections.abc import Callable
from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
__all__ = ['NativeCategoryRealization', 'NativeFunctorRealization', 'NativeTransformationRealization', 'NativeObjectRealization', 'NativeMorphismRealization', 'NativeUniversalPresentationRealization', 'NativeObjectRealizations', 'NativeMorphismRealizations', 'NativeUniversalPresentationRealizations', 'retain_native_category', 'has_native_category', 'native_category', 'retain_native_functor', 'has_native_functor', 'native_functor', 'retain_native_transformation', 'has_native_transformation', 'native_transformation', 'retain_native_universal_presentation', 'native_universal_presentation']

@dataclass(frozen=True, eq=False, slots=True)
class NativeCategoryRealization[Native]:
    owner: Category
    native: Native

@dataclass(frozen=True, eq=False, slots=True)
class NativeFunctorRealization[Native]:
    value: MorphismCategory.ObjectType
    source: Category
    target: Category
    native: Native

@dataclass(frozen=True, eq=False, slots=True)
class NativeTransformationRealization[Native]:
    value: MorphismCategory.ObjectType
    source: MorphismCategory.ObjectType
    target: MorphismCategory.ObjectType
    native: Native

@dataclass(frozen=True, eq=False, slots=True)
class NativeObjectRealization[Native, Construction]:
    owner: Category
    value: CategoryOfCategories.ElementType
    native: Native
    construction: Construction

@dataclass(frozen=True, eq=False, slots=True)
class NativeMorphismRealization[Native]:
    owner: Category
    value: MorphismCategory.ObjectType
    source: CategoryOfCategories.ElementType
    target: CategoryOfCategories.ElementType
    native: Native

@dataclass(frozen=True, eq=False, slots=True)
class NativeUniversalPresentationRealization[NativeDiagram, NativePresentation]:
    owner: Category
    diagram: Functor
    presentation: CategoryOfCategories.ElementType
    native_diagram: NativeDiagram
    object_correspondence: tuple[tuple[CategoryOfCategories.ElementType, object], ...]
    arrow_correspondence: tuple[tuple[MorphismCategory.ObjectType, object], ...]
    native_presentation: NativePresentation
    native_apex: object
    native_legs: tuple[tuple[CategoryOfCategories.ElementType, object], ...]
    mediator: Callable[[object], object]

class _IdentityRecords[Record]:

    def __init__(self) -> None:
        ...

    def retain(self, key: object, record: Record) -> None:
        ...

    def has(self, key: object) -> bool:
        ...

    def get(self, key: object) -> Record:
        ...

class NativeObjectRealizations[Native, Construction]:

    def __init__(self) -> None:
        ...

    def retain(self, owner: Category, value: CategoryOfCategories.ElementType, native: Native, construction: Construction) -> NativeObjectRealization[Native, Construction]:
        ...

    def has(self, value: CategoryOfCategories.ElementType) -> bool:
        ...

    def realization(self, value: CategoryOfCategories.ElementType) -> NativeObjectRealization[Native, Construction]:
        ...

class NativeMorphismRealizations[Native]:

    def __init__(self) -> None:
        ...

    def retain(self, owner: Category, value: MorphismCategory.ObjectType, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, native: Native) -> NativeMorphismRealization[Native]:
        ...

    def has(self, value: MorphismCategory.ObjectType) -> bool:
        ...

    def realization(self, value: MorphismCategory.ObjectType) -> NativeMorphismRealization[Native]:
        ...

class NativeUniversalPresentationRealizations[NativeDiagram, NativePresentation]:

    def __init__(self) -> None:
        ...

    def retain(self, owner: Category, diagram: Functor, presentation: CategoryOfCategories.ElementType, native_diagram: NativeDiagram, object_correspondence: tuple[tuple[CategoryOfCategories.ElementType, object], ...], arrow_correspondence: tuple[tuple[MorphismCategory.ObjectType, object], ...], native_presentation: NativePresentation, native_apex: object, native_legs: tuple[tuple[CategoryOfCategories.ElementType, object], ...], mediator: Callable[[object], object]) -> NativeUniversalPresentationRealization[NativeDiagram, NativePresentation]:
        ...

    def has(self, presentation: CategoryOfCategories.ElementType) -> bool:
        ...

    def realization(self, presentation: CategoryOfCategories.ElementType) -> NativeUniversalPresentationRealization[NativeDiagram, NativePresentation]:
        ...

def retain_native_category(owner: Category, native: object) -> NativeCategoryRealization[object]:
    ...

def has_native_category(owner: Category) -> bool:
    ...

def native_category(owner: Category) -> NativeCategoryRealization[object]:
    ...

def retain_native_functor(value: MorphismCategory.ObjectType, source: Category, target: Category, native: object) -> NativeFunctorRealization[object]:
    ...

def has_native_functor(value: MorphismCategory.ObjectType) -> bool:
    ...

def native_functor(value: MorphismCategory.ObjectType) -> NativeFunctorRealization[object]:
    ...

def retain_native_transformation(value: MorphismCategory.ObjectType, source: MorphismCategory.ObjectType, target: MorphismCategory.ObjectType, native: object) -> NativeTransformationRealization[object]:
    ...

def has_native_transformation(value: MorphismCategory.ObjectType) -> bool:
    ...

def native_transformation(value: MorphismCategory.ObjectType) -> NativeTransformationRealization[object]:
    ...

def retain_native_universal_presentation(owner: Category, diagram: Functor, presentation: CategoryOfCategories.ElementType, native_diagram: object, object_correspondence: tuple[tuple[CategoryOfCategories.ElementType, object], ...], arrow_correspondence: tuple[tuple[MorphismCategory.ObjectType, object], ...], native_presentation: object, native_apex: object, native_legs: tuple[tuple[CategoryOfCategories.ElementType, object], ...], mediator: Callable[[object], object]) -> NativeUniversalPresentationRealization[object, object]:
    ...

def native_universal_presentation(presentation: CategoryOfCategories.ElementType) -> NativeUniversalPresentationRealization[object, object]:
    ...
