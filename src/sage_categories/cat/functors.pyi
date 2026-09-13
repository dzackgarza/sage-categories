from collections.abc import Callable
from dataclasses import dataclass
from typing import overload

from _typeshed import Incomplete

import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.cat.properties
import sage_categories.kernel.roles
from sage_categories.cat.category import Assignment as Assignment
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.category import OnMorphism as OnMorphism
from sage_categories.cat.category import OnObject as OnObject
from sage_categories.cat.morphisms import FixedEndpointCategory as FixedEndpointCategory
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.morphisms import endpoints as endpoints
from sage_categories.cat.predicates import Axiom as Axiom
from sage_categories.cat.predicates import Predicate as Predicate
from sage_categories.cat.predicates import Proposition as Proposition
from sage_categories.cat.predicates import Unknown as Unknown
from sage_categories.cat.predicates import UnknownClass as UnknownClass
from sage_categories.cat.predicates import ask as ask
from sage_categories.cat.predicates import conjunction as conjunction
from sage_categories.cat.predicates import decide as decide
from sage_categories.cat.predicates import register_handler as register_handler
from sage_categories.cat.properties import (
    FixedEndpointProperty as FixedEndpointProperty,
)
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.kernel.refinement import is_placed as is_placed
from sage_categories.kernel.refinement import is_subcategory as is_subcategory
from sage_categories.kernel.refinement import refine as refine
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import LazyFamily as LazyFamily
from sage_categories.kernel.sage_runtime import cached_method as cached_method

__all__ = ["CreatesLimitsCategory", "Fun", "Functor", "FunctorCategory", "FunctorProperty", "FunctorsCategory", "NaturalTransformation", "PreservesLimitsCategory"]

@dataclass(frozen=True, eq=False, slots=True)
class NaturalTransformationData:
    assignment: Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType]
    source: CategoryOfCategories.MorphismType
    target: CategoryOfCategories.MorphismType

type Functor = sage_categories.cat.category.CategoryOfCategories.MorphismType

class ShapeIndexedFunctorProperty(PropertySubcategory[[OnObject, OnMorphism], [Assignment]]):
    def __init__(self, ambient: FunctorsCategory, name: str, full_subcategory_of: tuple[Category, ...], shape: Category | Functor) -> None: ...
    def shape(self) -> Category | Functor: ...

class _StaticRoles_FunctorProperty(sage_categories.cat.properties._StaticRoles_FixedEndpointProperty):
    class ObjectType(_StaticRoles_FunctorCategory.ObjectType): ...
    class ElementType(_StaticRoles_FunctorCategory.ElementType): ...

    class MorphismType(_StaticRoles_FunctorCategory.MorphismType):
        def domain(self) -> FunctorProperty.ObjectType: ...
        def codomain(self) -> FunctorProperty.ObjectType: ...

class FunctorProperty(
    _StaticRoles_FunctorProperty,
    FixedEndpointProperty[
        [OnObject, OnMorphism], [Assignment], _StaticRoles_FunctorProperty.ObjectType, _StaticRoles_FunctorProperty.ElementType, _StaticRoles_FunctorProperty.MorphismType
    ],
):
    def __call__(self, *args: OnObject | OnMorphism, **kwargs: OnObject | OnMorphism) -> Functor: ...

class _StaticRoles_FunctorCategory(sage_categories.cat.morphisms._StaticRoles_FixedEndpointCategory):
    class ObjectType[
        DomainCategory = Category[..., ...],
        CodomainCategory = Category[..., ...],
        DomainObject = sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType,
        DomainElement = sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType,
        DomainMorphism = sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType,
        CodomainObject = sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType,
        CodomainElement = sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType,
        CodomainMorphism = sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType,
    ](
        sage_categories.cat.category._StaticRoles_CategoryOfCategories.MorphismType[
            DomainCategory, CodomainCategory, DomainObject, DomainElement, DomainMorphism, CodomainObject, CodomainElement, CodomainMorphism
        ],
        sage_categories.kernel.roles.ObjectOfCategory,
    ): ...
    class ElementType(_StaticRoles_FunctorsCategory.ElementType): ...

    class MorphismType(_StaticRoles_FunctorsCategory.MorphismType):
        def domain(self) -> FunctorCategory.ObjectType: ...
        def codomain(self) -> FunctorCategory.ObjectType: ...

class FunctorCategory[
    DomainCategory = Category[..., ...],
    CodomainCategory = Category[..., ...],
    DomainObject = sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType,
    DomainElement = sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType,
    DomainMorphism = sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType,
    CodomainObject = sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType,
    CodomainElement = sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType,
    CodomainMorphism = sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType,
](
    _StaticRoles_FunctorCategory,
    FixedEndpointCategory[
        [OnObject, OnMorphism],
        [Assignment],
        DomainCategory,
        CodomainCategory,
        _StaticRoles_FunctorCategory.ObjectType[
            DomainCategory, CodomainCategory, DomainObject, DomainElement, DomainMorphism, CodomainObject, CodomainElement, CodomainMorphism
        ],
        _StaticRoles_FunctorCategory.ElementType,
        _StaticRoles_FunctorCategory.MorphismType,
    ],
):
    def __init__(self, morphisms: MorphismCategory, domain: DomainCategory, codomain: CodomainCategory) -> None: ...
    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition: ...
    def diagram(self, value: CategoryOfCategories.ElementType) -> Functor: ...
    def construct_morphism(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, assignment: Assignment) -> NaturalTransformation: ...
    def construct_identity(self, value: CategoryOfCategories.ElementType) -> NaturalTransformation: ...
    def evaluation(self, vertex: CategoryOfCategories.ElementType) -> Functor: ...
    def ev(self, vertex: CategoryOfCategories.ElementType | int) -> Functor: ...
    def constant(self, value: CategoryOfCategories.ElementType) -> Functor: ...
    def Terminal(self) -> Functor: ...
    def diagonal(self) -> Functor: ...
    def TotalCones(self) -> Category: ...
    def has_constant_value(self, diagram: Functor) -> bool: ...
    def constant_value(self, diagram: Functor) -> CategoryOfCategories.ElementType: ...
    def from_object_rule(self, rule: OnObject) -> Functor: ...
    def object_set(self) -> CategoryOfCategories.ElementType: ...
    def object_at(self, point: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType: ...
    def morphism_at(self, point: CategoryOfCategories.ElementType) -> NaturalTransformation: ...
    def narrowing_type(self) -> type[FunctorProperty]: ...

class _StaticRoles_FunctorsCategory(sage_categories.cat.morphisms._StaticRoles_MorphismCategory):
    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def __init__(self, data: NaturalTransformationData) -> None: ...
        def source_functor(self) -> Functor: ...
        def target_functor(self) -> Functor: ...
        def component(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType: ...
        def op(self) -> NaturalTransformation: ...
        def whisker_left(self, functor: Functor) -> NaturalTransformation: ...
        def whisker_right(self, functor: Functor) -> NaturalTransformation: ...
        def horizontal(self, transformation: NaturalTransformation) -> NaturalTransformation: ...
        def domain(self) -> FunctorsCategory.ObjectType: ...
        def codomain(self) -> FunctorsCategory.ObjectType: ...

class FunctorsCategory(
    _StaticRoles_FunctorsCategory,
    MorphismCategory[
        [OnObject, OnMorphism], [Assignment], CategoryOfCategories.MorphismType, _StaticRoles_FunctorsCategory.ElementType, _StaticRoles_FunctorsCategory.MorphismType
    ],
):
    ObjectType = CategoryOfCategories.MorphismType

    def __init__(self, base: CategoryOfCategories) -> None: ...
    def fixed_endpoint_type(self) -> type[FunctorCategory]: ...
    @overload
    def __call__[DomainObject, DomainElement, DomainMorphism, CodomainObject, CodomainElement, CodomainMorphism](
        self, shape: Category[..., ..., DomainObject, DomainElement, DomainMorphism], target: Category[..., ..., CodomainObject, CodomainElement, CodomainMorphism]
    ) -> FunctorCategory[
        Category[..., ..., DomainObject, DomainElement, DomainMorphism],
        Category[..., ..., CodomainObject, CodomainElement, CodomainMorphism],
        DomainObject,
        DomainElement,
        DomainMorphism,
        CodomainObject,
        CodomainElement,
        CodomainMorphism,
    ]: ...
    @overload
    def __call__(self, shape: Category[..., ...], target: Functor) -> Functor: ...
    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition: ...
    Full: Incomplete
    Faithful: Incomplete
    EssentiallySurjective: Incomplete
    FullyFaithful: Incomplete
    Equivalences: Incomplete
    Isofibrations: Incomplete
    Monomorphisms: Incomplete
    Fibrations: Incomplete
    Opfibrations: Incomplete
    PreservesLimits: Incomplete
    CreatesLimits: Incomplete

    def identity_on_values(self, source: Category, target: Category) -> Functor: ...
    def declares_inheritance(self, functor: Functor) -> bool: ...
    def declares_subcategory(self, functor: Functor) -> bool: ...
    def declares_point(self, functor: Functor) -> bool: ...
    def subcategory_monomorphism(self, source: Category, target: Category) -> Functor: ...
    def full_subcategory_monomorphism(self, source: Category, target: Category) -> Functor: ...
    def limit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]: ...

class PreservesLimitsCategory(ShapeIndexedFunctorProperty): ...
class CreatesLimitsCategory(ShapeIndexedFunctorProperty): ...

Fun: FunctorsCategory
type NaturalTransformation = FunctorsCategory.MorphismType

def diagram_of(value: CategoryOfCategories.ElementType) -> Functor: ...

Cat: Incomplete
