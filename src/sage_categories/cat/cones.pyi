import sage_categories
from _typeshed import Incomplete
from collections.abc import Callable, Hashable
from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import PropertySubcategory
__all__ = ['cone', 'cocone', 'cone_apex', 'cocone_apex', 'vertex_of', 'ConeCategory', 'LimitConesCategory', 'cones', 'limit_cones', 'cocones', 'colimit_cocones']
type Components = Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType]
type Lift = Callable[[ConeCategory.ObjectType], MorphismCategory.ObjectType]

def cone(diagram: Functor, apex: CategoryOfCategories.ElementType, components: Components) -> NaturalTransformation:
    ...

def cocone(diagram: Functor, apex: CategoryOfCategories.ElementType, components: Components) -> NaturalTransformation:
    ...

def cone_apex(transformation: NaturalTransformation) -> CategoryOfCategories.ElementType:
    ...

def cocone_apex(transformation: NaturalTransformation) -> CategoryOfCategories.ElementType:
    ...

def vertex_of(shape: Category, index: CategoryOfCategories.ElementType | Hashable) -> CategoryOfCategories.ElementType:
    ...

@dataclass(frozen=True, eq=False, slots=True)
class ConeData:
    transformation: NaturalTransformation
    dual: bool = ...

@dataclass(frozen=True, eq=False, slots=True)
class ConeMorphismData:
    apex_morphism: MorphismCategory.ObjectType

class ConeCategory(Category[[MorphismCategory.ObjectType], []]):
    LimitCones: Incomplete
    ColimitCocones: Incomplete

    class ObjectType(sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, data: ConeData) -> None:
            ...

        def diagram(self) -> Functor:
            ...

        def apex(self) -> CategoryOfCategories.ElementType:
            ...

        def leg(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            ...

        def transformation(self) -> NaturalTransformation:
            ...

    class ElementType(sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: ConeMorphismData) -> None:
            ...

        def apex_morphism(self) -> MorphismCategory.ObjectType:
            ...

    def __init__(self, diagram: Functor, dual: bool=False) -> None:
        ...

    def diagram(self) -> Functor:
        ...

    def __call__(self, transformation: NaturalTransformation) -> ConeCategory.ObjectType:
        ...

    def construct_morphism(self, source: ConeCategory.ObjectType, target: ConeCategory.ObjectType, apex_morphism: MorphismCategory.ObjectType) -> ConeCategory.MorphismType:
        ...

    def construct_identity(self, member_object: ConeCategory.ObjectType) -> ConeCategory.MorphismType:
        ...

    def composite(self, second: ConeCategory.MorphismType, first: ConeCategory.MorphismType) -> ConeCategory.MorphismType:
        ...

    def apex_functor(self) -> Functor:
        ...

class LimitConesCategory(PropertySubcategory[[MorphismCategory.ObjectType], []]):

    class ObjectType(sage_categories.cat.cones.ConeCategory.ObjectType, sage_categories.kernel.roles.ObjectOfCategory):

        def lift(self, candidate: ConeCategory.ObjectType) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.cones.ConeCategory.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.cones.ConeCategory.MorphismType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def with_universal_data(self, transformation: NaturalTransformation, lift: Lift) -> LimitConesCategory.ObjectType:
        ...

def cones(diagram: Functor) -> ConeCategory:
    ...

def limit_cones(diagram: Functor) -> LimitConesCategory:
    ...

def cocones(diagram: Functor) -> ConeCategory:
    ...

def colimit_cocones(diagram: Functor) -> LimitConesCategory:
    ...
