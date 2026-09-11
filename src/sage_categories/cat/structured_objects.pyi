import sage_categories.cat.cat_constructions
import sage_categories.cat.category
import sage_categories.cat.constructions
import sage_categories.cat.morphisms
import sage_categories.cat.properties
import sage_categories.cat.structured_objects
import sage_categories.kernel.roles
import sage_categories.sets.finite
from _typeshed import Incomplete
from functools import cache, partial
from sage_categories.cat.cat_constructions import FamilyObjectData, LimitSubcategory
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.monoidal import MonoidalStructuresCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate
from sage_categories.cat.properties import FullSubcategory, PropertySubcategory
from sage_categories.kernel.sage_runtime import cached_method
__all__ = ['InserterCategory', 'Inserter', 'EquifierCategory', 'Equifier', 'EndofunctorAlgebras', 'MagmaCategory', 'Magmas', 'PointedMagmas', 'MonoidCategory', 'Monoids', 'GroupsCategory', 'Groups', 'AdditiveMagmasCategory', 'MultiplicativeMagmasCategory', 'AdditiveMonoidsCategory', 'MultiplicativeMonoidsCategory', 'AdditiveGroupsCategory', 'AdditiveGroups', 'AdditiveMagmas', 'MultiplicativeMagmas', 'AdditiveMonoids', 'MultiplicativeMonoids', 'MonoidPairsCategory', 'SemiringCategory', 'Semirings', 'RingCategory', 'Rings', 'EilenbergMoore']

class InserterCategory(LimitSubcategory):

    class ObjectType(sage_categories.cat.structured_objects.MagmaCategory.ObjectType):

        def carrier(self) -> CategoryOfCategories.ElementType:
            ...

        def structure(self) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.structured_objects.MagmaCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.structured_objects.MagmaCategory.MorphismType):

        def underlying_morphism(self) -> MorphismCategory.ObjectType:
            ...

        def domain(self) -> InserterCategory.ObjectType:
            ...

        def codomain(self) -> InserterCategory.ObjectType:
            ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def algebra(self, carrier: CategoryOfCategories.ElementType, structure: MorphismCategory.ObjectType) -> InserterCategory.ObjectType:
        ...

    def homomorphism(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, arrow: MorphismCategory.ObjectType) -> InserterCategory.MorphismType:
        ...

    @cached_method
    def forgetful(self) -> Functor:
        ...

    @cached_method
    def defining_transformation(self) -> NaturalTransformation:
        ...

def Inserter(first: Functor, second: Functor, category_type: type[InserterCategory] | partial[InserterCategory]=...) -> InserterCategory:
    ...

class EquifierCategory(FullSubcategory):

    class ObjectType(sage_categories.cat.cat_constructions.LimitCategory.ObjectType, sage_categories.sets.finite.SetsCategory.ObjectType, sage_categories.cat.constructions.LimitsCategory.ElementType):
        ...

    class ElementType(sage_categories.cat.cat_constructions.LimitCategory.ElementType, sage_categories.sets.finite.SetsCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.cat_constructions.LimitCategory.MorphismType, sage_categories.sets.finite.SetsCategory.MorphismType):
        ...

        def domain(self) -> EquifierCategory.ObjectType:
            ...

        def codomain(self) -> EquifierCategory.ObjectType:
            ...

    def __init__(self, first: NaturalTransformation, second: NaturalTransformation) -> None:
        ...

    def __call__(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

def Equifier(first: NaturalTransformation, second: NaturalTransformation) -> EquifierCategory:
    ...

def EndofunctorAlgebras(endofunctor: Functor) -> InserterCategory:
    ...

class _CommutativePredicate(Predicate):
    name: str

class _GroupPredicate(Predicate):
    name: str

class MagmaCategory(InserterCategory):

    class ObjectType(sage_categories.cat.cat_constructions.LimitCategory.ObjectType, sage_categories.sets.finite.SetsCategory.ObjectType, sage_categories.cat.constructions.LimitsCategory.ElementType):

        def carrier(self) -> CategoryOfCategories.ElementType:
            ...

        def structure(self) -> MorphismCategory.ObjectType:
            ...

        def operation(self) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.cat_constructions.LimitCategory.ElementType, sage_categories.sets.finite.SetsCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.cat_constructions.LimitCategory.MorphismType, sage_categories.sets.finite.SetsCategory.MorphismType):

        def underlying_morphism(self) -> MorphismCategory.ObjectType:
            ...

        def domain(self) -> MagmaCategory.ObjectType:
            ...

        def codomain(self) -> MagmaCategory.ObjectType:
            ...

    def __init__(self, diagram: Functor, tensor: Functor) -> None:
        ...

    def tensor(self) -> Functor:
        ...
    Commutative: Incomplete

def Magmas(structure: Functor | MonoidalStructuresCategory.ObjectType) -> MagmaCategory:
    ...

def PointedMagmas(tensor: Functor, unit: CategoryOfCategories.ElementType) -> InserterCategory:
    ...

class MonoidCategory(EquifierCategory):

    class ObjectType(sage_categories.cat.structured_objects.EquifierCategory.ObjectType, sage_categories.cat.structured_objects.InserterCategory.ObjectType):

        def operation(self) -> MorphismCategory.ObjectType:
            ...

        def unit_morphism(self) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.structured_objects.EquifierCategory.ElementType, sage_categories.cat.structured_objects.InserterCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.structured_objects.EquifierCategory.MorphismType, sage_categories.cat.structured_objects.InserterCategory.MorphismType):
        ...

        def domain(self) -> MonoidCategory.ObjectType:
            ...

        def codomain(self) -> MonoidCategory.ObjectType:
            ...

    def __init__(self, first: NaturalTransformation, second: NaturalTransformation, monoidal: MonoidalStructuresCategory.ObjectType) -> None:
        ...

    def monoidal_structure(self) -> MonoidalStructuresCategory.ObjectType:
        ...
    Group: Incomplete

    def homomorphism(self, source: MonoidCategory.ObjectType, target: MonoidCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def __call__(self, operation: MorphismCategory.ObjectType, unit: MorphismCategory.ObjectType) -> MonoidCategory.ObjectType:
        ...

    @cached_method
    def to_magmas(self) -> Functor:
        ...

def Monoids(structure: Category | MonoidalStructuresCategory.ObjectType) -> MonoidCategory:
    ...

class GroupsCategory(PropertySubcategory):

    class ObjectType(sage_categories.cat.structured_objects.MonoidCategory.ObjectType):

        @cache
        def inversion(self) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.structured_objects.MonoidCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.structured_objects.MonoidCategory.MorphismType):
        ...

        def domain(self) -> GroupsCategory.ObjectType:
            ...

        def codomain(self) -> GroupsCategory.ObjectType:
            ...

def Groups(structure: Category | MonoidalStructuresCategory.ObjectType) -> GroupsCategory:
    ...

class NamedOperationCategory(LimitSubcategory):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> NamedOperationCategory.ObjectType:
            ...

        def codomain(self) -> NamedOperationCategory.ObjectType:
            ...
    Commutative: Incomplete

    def neutral_category(self) -> Category:
        ...

    def symbol_category(self) -> Category:
        ...

    def symbol(self) -> CategoryOfCategories.ElementType:
        ...

    def renamed(self, neutral_object: CategoryOfCategories.ElementType) -> NamedOperationCategory.ObjectType:
        ...

    def homomorphism(self, source: NamedOperationCategory.ObjectType, target: NamedOperationCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> NamedOperationCategory.MorphismType:
        ...

    @cached_method
    def to_carrier(self) -> Functor:
        ...

    @cached_method
    def to_named_magmas(self) -> Functor:
        ...

    def named_magmas(self) -> NamedOperationCategory:
        ...

    @cached_method
    def to_named_monoids(self) -> Functor:
        ...

    def named_monoids(self) -> NamedOperationCategory:
        ...

class AdditiveMagmasCategory(NamedOperationCategory):

    class ObjectType(sage_categories.cat.cat_constructions.LimitCategory.ObjectType, sage_categories.sets.finite.SetsCategory.ObjectType, sage_categories.cat.constructions.LimitsCategory.ElementType, sage_categories.cat.constructions.ProductsCategory.ElementType):

        def __init__(self, data: FamilyObjectData) -> None:
            ...

        def addition(self) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.cat_constructions.LimitCategory.ElementType, sage_categories.sets.finite.SetsCategory.ElementType):

        def __add__(self, other: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            ...

    class MorphismType(sage_categories.cat.cat_constructions.LimitCategory.MorphismType, sage_categories.sets.finite.SetsCategory.MorphismType):
        ...

        def domain(self) -> AdditiveMagmasCategory.ObjectType:
            ...

        def codomain(self) -> AdditiveMagmasCategory.ObjectType:
            ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

class MultiplicativeMagmasCategory(NamedOperationCategory):

    class ObjectType(sage_categories.cat.cat_constructions.LimitCategory.ObjectType, sage_categories.sets.finite.SetsCategory.ObjectType, sage_categories.cat.constructions.LimitsCategory.ElementType, sage_categories.cat.constructions.ProductsCategory.ElementType):

        def __init__(self, data: FamilyObjectData) -> None:
            ...

        def multiplication(self) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.cat_constructions.LimitCategory.ElementType, sage_categories.sets.finite.SetsCategory.ElementType):

        def __mul__(self, other: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            ...

    class MorphismType(sage_categories.cat.cat_constructions.LimitCategory.MorphismType, sage_categories.sets.finite.SetsCategory.MorphismType):
        ...

        def domain(self) -> MultiplicativeMagmasCategory.ObjectType:
            ...

        def codomain(self) -> MultiplicativeMagmasCategory.ObjectType:
            ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

class NamedMonoidsCategory(NamedOperationCategory):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> NamedMonoidsCategory.ObjectType:
            ...

        def codomain(self) -> NamedMonoidsCategory.ObjectType:
            ...
    Group: Incomplete

class AdditiveMonoidsCategory(NamedMonoidsCategory):

    class ObjectType(sage_categories.cat.structured_objects.AdditiveMagmasCategory.ObjectType):

        def __init__(self, data: FamilyObjectData) -> None:
            ...

        def zero(self) -> CategoryOfCategories.ElementType:
            ...

    class ElementType(sage_categories.cat.structured_objects.AdditiveMagmasCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.structured_objects.AdditiveMagmasCategory.MorphismType):
        ...

        def domain(self) -> AdditiveMonoidsCategory.ObjectType:
            ...

        def codomain(self) -> AdditiveMonoidsCategory.ObjectType:
            ...

    def named_magmas(self) -> AdditiveMagmasCategory:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

class MultiplicativeMonoidsCategory(NamedMonoidsCategory):

    class ObjectType(sage_categories.cat.structured_objects.MultiplicativeMagmasCategory.ObjectType):

        def __init__(self, data: FamilyObjectData) -> None:
            ...

        def one(self) -> CategoryOfCategories.ElementType:
            ...

    class ElementType(sage_categories.cat.structured_objects.MultiplicativeMagmasCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.structured_objects.MultiplicativeMagmasCategory.MorphismType):
        ...

        def domain(self) -> MultiplicativeMonoidsCategory.ObjectType:
            ...

        def codomain(self) -> MultiplicativeMonoidsCategory.ObjectType:
            ...

    def named_magmas(self) -> MultiplicativeMagmasCategory:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

class AdditiveGroupsCategory(NamedOperationCategory):

    class ObjectType(sage_categories.cat.structured_objects.AdditiveMonoidsCategory.ObjectType):

        def __init__(self, data: FamilyObjectData) -> None:
            ...

        def negation(self) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.structured_objects.AdditiveMonoidsCategory.ElementType):

        def __neg__(self) -> CategoryOfCategories.ElementType:
            ...

        def __sub__(self, other: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            ...

    class MorphismType(sage_categories.cat.structured_objects.AdditiveMonoidsCategory.MorphismType):
        ...

        def domain(self) -> AdditiveGroupsCategory.ObjectType:
            ...

        def codomain(self) -> AdditiveGroupsCategory.ObjectType:
            ...

    def named_monoids(self) -> AdditiveMonoidsCategory:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

def AdditiveGroups(structure: Category | MonoidalStructuresCategory.ObjectType) -> AdditiveGroupsCategory:
    ...

def AdditiveMagmas(structure: Functor | MonoidalStructuresCategory.ObjectType) -> AdditiveMagmasCategory:
    ...

def MultiplicativeMagmas(structure: Functor | MonoidalStructuresCategory.ObjectType) -> MultiplicativeMagmasCategory:
    ...

def AdditiveMonoids(structure: Category | MonoidalStructuresCategory.ObjectType) -> AdditiveMonoidsCategory:
    ...

def MultiplicativeMonoids(structure: Category | MonoidalStructuresCategory.ObjectType) -> MultiplicativeMonoidsCategory:
    ...

class MonoidPairsCategory(LimitSubcategory):

    class ObjectType(sage_categories.cat.properties.InverseImageSubcategory.ObjectType, sage_categories.cat.structured_objects.MultiplicativeMonoidsCategory.ObjectType, sage_categories.cat.structured_objects.AdditiveMonoidsCategory.ObjectType):
        ...

    class ElementType(sage_categories.cat.properties.InverseImageSubcategory.ElementType, sage_categories.cat.structured_objects.MultiplicativeMonoidsCategory.ElementType, sage_categories.cat.structured_objects.AdditiveMonoidsCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.properties.InverseImageSubcategory.MorphismType, sage_categories.cat.structured_objects.MultiplicativeMonoidsCategory.MorphismType, sage_categories.cat.structured_objects.AdditiveMonoidsCategory.MorphismType):
        ...

        def domain(self) -> MonoidPairsCategory.ObjectType:
            ...

        def codomain(self) -> MonoidPairsCategory.ObjectType:
            ...

    @cached_method
    def to_additive(self) -> Functor:
        ...

    @cached_method
    def to_multiplicative(self) -> Functor:
        ...

    @cached_method
    def to_carrier(self) -> Functor:
        ...

    def homomorphism(self, source: MonoidPairsCategory.ObjectType, target: MonoidPairsCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> MonoidPairsCategory.MorphismType:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

class SemiringCategory(EquifierCategory):

    class ObjectType(sage_categories.cat.structured_objects.EquifierCategory.ObjectType, sage_categories.cat.structured_objects.MonoidPairsCategory.ObjectType):
        ...

    class ElementType(sage_categories.cat.structured_objects.EquifierCategory.ElementType, sage_categories.cat.structured_objects.MonoidPairsCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.structured_objects.EquifierCategory.MorphismType, sage_categories.cat.structured_objects.MonoidPairsCategory.MorphismType):
        ...

        def domain(self) -> SemiringCategory.ObjectType:
            ...

        def codomain(self) -> SemiringCategory.ObjectType:
            ...

    def __init__(self, first: NaturalTransformation, second: NaturalTransformation, monoidal: MonoidalStructuresCategory.ObjectType, pairs: MonoidPairsCategory) -> None:
        ...

    def monoidal_structure(self) -> MonoidalStructuresCategory.ObjectType:
        ...

    @cached_method
    def to_additive(self) -> Functor:
        ...

    @cached_method
    def to_multiplicative(self) -> Functor:
        ...

    @cached_method
    def to_carrier(self) -> Functor:
        ...

    def homomorphism(self, source: SemiringCategory.ObjectType, target: SemiringCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> SemiringCategory.MorphismType:
        ...

    def __call__(self, addition: MorphismCategory.ObjectType, zero: MorphismCategory.ObjectType, multiplication: MorphismCategory.ObjectType, one: MorphismCategory.ObjectType) -> SemiringCategory.ObjectType:
        ...

def Semirings(base: Category) -> SemiringCategory:
    ...

class RingCategory(LimitSubcategory):

    class ObjectType(sage_categories.cat.structured_objects.SemiringCategory.ObjectType, sage_categories.cat.structured_objects.AdditiveGroupsCategory.ObjectType):
        ...

    class ElementType(sage_categories.cat.structured_objects.SemiringCategory.ElementType, sage_categories.cat.structured_objects.AdditiveGroupsCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.structured_objects.SemiringCategory.MorphismType, sage_categories.cat.structured_objects.AdditiveGroupsCategory.MorphismType):
        ...

        def domain(self) -> RingCategory.ObjectType:
            ...

        def codomain(self) -> RingCategory.ObjectType:
            ...

    def __init__(self, diagram: Functor, monoidal: MonoidalStructuresCategory.ObjectType) -> None:
        ...

    def monoidal_structure(self) -> MonoidalStructuresCategory.ObjectType:
        ...

    @cached_method
    def to_semiring(self) -> Functor:
        ...

    @cached_method
    def to_additive_group(self) -> Functor:
        ...

    @cached_method
    def forgetful(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def __call__(self, addition: MorphismCategory.ObjectType, zero: MorphismCategory.ObjectType, multiplication: MorphismCategory.ObjectType, one: MorphismCategory.ObjectType) -> RingCategory.ObjectType:
        ...

    def homomorphism(self, source: RingCategory.ObjectType, target: RingCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> RingCategory.MorphismType:
        ...

    def opposite_ring(self, ring: RingCategory.ObjectType) -> RingCategory.ObjectType:
        ...

    @cached_method
    def opposite_functor(self) -> Functor:
        ...

def Rings(base: Category) -> RingCategory:
    ...

def EilenbergMoore(endofunctor: Functor, unit: NaturalTransformation, multiplication: NaturalTransformation) -> EquifierCategory:
    ...
