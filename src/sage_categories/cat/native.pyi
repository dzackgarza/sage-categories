from collections.abc import Callable

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory

class NativeObjectRealization[Native, Construction]:
    owner: Category
    value: CategoryOfCategories.ElementType
    native: Native
    construction: Construction

class NativeMorphismRealization[Native]:
    owner: Category
    value: MorphismCategory.ObjectType
    source: CategoryOfCategories.ElementType
    target: CategoryOfCategories.ElementType
    native: Native

class NativeObjectRealizations[Native, Construction]:
    def __init__(self) -> None: ...
    def retain(self, owner: Category, value: CategoryOfCategories.ElementType, native: Native, construction: Construction) -> NativeObjectRealization[Native, Construction]: ...
    def has(self, value: CategoryOfCategories.ElementType) -> bool: ...
    def realization(self, value: CategoryOfCategories.ElementType) -> NativeObjectRealization[Native, Construction]: ...

class NativeMorphismRealizations[Native]:
    def __init__(self) -> None: ...
    def retain(self, owner: Category, value: MorphismCategory.ObjectType, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, native: Native) -> NativeMorphismRealization[Native]: ...
    def has(self, value: MorphismCategory.ObjectType) -> bool: ...
    def realization(self, value: MorphismCategory.ObjectType) -> NativeMorphismRealization[Native]: ...

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

class NativeUniversalPresentationRealizations[NativeDiagram, NativePresentation]:
    def __init__(self) -> None: ...
    def retain(self, owner: Category, diagram: Functor, presentation: CategoryOfCategories.ElementType, native_diagram: NativeDiagram, object_correspondence: tuple[tuple[CategoryOfCategories.ElementType, object], ...], arrow_correspondence: tuple[tuple[MorphismCategory.ObjectType, object], ...], native_presentation: NativePresentation, native_apex: object, native_legs: tuple[tuple[CategoryOfCategories.ElementType, object], ...], mediator: Callable[[object], object]) -> NativeUniversalPresentationRealization[NativeDiagram, NativePresentation]: ...
    def has(self, presentation: CategoryOfCategories.ElementType) -> bool: ...
    def realization(self, presentation: CategoryOfCategories.ElementType) -> NativeUniversalPresentationRealization[NativeDiagram, NativePresentation]: ...

def retain_native_universal_presentation(owner: Category, diagram: Functor, presentation: CategoryOfCategories.ElementType, native_diagram: object, object_correspondence: tuple[tuple[CategoryOfCategories.ElementType, object], ...], arrow_correspondence: tuple[tuple[MorphismCategory.ObjectType, object], ...], native_presentation: object, native_apex: object, native_legs: tuple[tuple[CategoryOfCategories.ElementType, object], ...], mediator: Callable[[object], object]) -> NativeUniversalPresentationRealization[object, object]: ...
def native_universal_presentation(presentation: CategoryOfCategories.ElementType) -> NativeUniversalPresentationRealization[object, object]: ...
