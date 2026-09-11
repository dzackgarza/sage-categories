import sage_categories.cat.properties
import sage_categories.cat.comma
import sage_categories.cat.cones
from _typeshed import Incomplete
from collections.abc import Callable, Hashable
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.comma import CommaSpecialization
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.sage_runtime import cached_method
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

class _StaticRoles_ConeCategory(sage_categories.cat.comma._StaticRoles_CommaSpecialization):

    class ObjectType(sage_categories.cat.comma.CommaCategory.ObjectType):

        def diagram(self) -> Functor:
            ...

        def apex(self) -> CategoryOfCategories.ElementType:
            ...

        def leg(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            ...

        def transformation(self) -> NaturalTransformation:
            ...

    class ElementType(sage_categories.cat.comma.CommaCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.comma.CommaCategory.MorphismType):

        def apex_morphism(self) -> MorphismCategory.ObjectType:
            ...

        def domain(self) -> ConeCategory.ObjectType:
            ...

        def codomain(self) -> ConeCategory.ObjectType:
            ...

class ConeCategory(_StaticRoles_ConeCategory, CommaSpecialization[_StaticRoles_ConeCategory.ObjectType, _StaticRoles_ConeCategory.ElementType, _StaticRoles_ConeCategory.MorphismType]):
    LimitCones: Incomplete
    ColimitCocones: Incomplete

    def __init__(self, diagram: Functor, dual: bool=False) -> None:
        ...

    def diagram(self) -> Functor:
        ...

    def apex_of(self, transformation: NaturalTransformation) -> CategoryOfCategories.ElementType:
        ...

    def __call__(self, transformation: NaturalTransformation) -> ConeCategory.ObjectType:
        ...

    def construct_morphism(self, source: ConeCategory.ObjectType, target: ConeCategory.ObjectType, apex_morphism: MorphismCategory.ObjectType) -> ConeCategory.MorphismType:
        ...

    @cached_method
    def apex_functor(self) -> Functor:
        ...

class _StaticRoles_LimitConesCategory(sage_categories.cat.properties._StaticRoles_PropertySubcategory):

    class ObjectType(sage_categories.cat.cones.ConeCategory.ObjectType):

        def lift(self, candidate: ConeCategory.ObjectType) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.cones.ConeCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.cones.ConeCategory.MorphismType):
        ...

        def domain(self) -> LimitConesCategory.ObjectType:
            ...

        def codomain(self) -> LimitConesCategory.ObjectType:
            ...

class LimitConesCategory(_StaticRoles_LimitConesCategory, PropertySubcategory[[MorphismCategory.ObjectType], [], _StaticRoles_LimitConesCategory.ObjectType, _StaticRoles_LimitConesCategory.ElementType, _StaticRoles_LimitConesCategory.MorphismType]):

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
