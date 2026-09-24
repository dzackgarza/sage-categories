import sage_categories.cat.cat_constructions
import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.cat.structured_objects
import sage_categories.kernel.roles
from sage_categories.cat.cat_constructions import LimitSubcategory as LimitSubcategory
from sage_categories.cat.cat_constructions import (
    limit_of_categories as limit_of_categories,
)
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.diagrams import cospan_diagram as cospan_diagram
from sage_categories.cat.functors import Cat as Cat
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.modules import ModuleCategory as ModuleCategory
from sage_categories.cat.modules import Modules as Modules
from sage_categories.cat.monoidal import (
    MonoidalStructuresCategory as MonoidalStructuresCategory,
)
from sage_categories.cat.monoidal import Reversed as Reversed
from sage_categories.cat.monoidal import SelfAction as SelfAction
from sage_categories.cat.monoidal import tensor_morphism as tensor_morphism
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.structured_objects import EquifierCategory as EquifierCategory
from sage_categories.cat.structured_objects import MonoidCategory as MonoidCategory
from sage_categories.cat.structured_objects import Monoids as Monoids
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function
from sage_categories.kernel.sage_runtime import cached_method as cached_method

__all__ = ["ActionPairsCategory", "BimoduleCategory", "Bimodules"]

class _StaticRoles_ActionPairsCategory(sage_categories.cat.cat_constructions._StaticRoles_LimitSubcategory):
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory): ...
    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def domain(self) -> ActionPairsCategory.ObjectType: ...
        def codomain(self) -> ActionPairsCategory.ObjectType: ...

class ActionPairsCategory(
    _StaticRoles_ActionPairsCategory,
    LimitSubcategory[_StaticRoles_ActionPairsCategory.ObjectType, _StaticRoles_ActionPairsCategory.ElementType, _StaticRoles_ActionPairsCategory.MorphismType],
):
    @cached_method
    def to_left(self) -> Functor: ...
    @cached_method
    def to_right(self) -> Functor: ...
    def homomorphism(
        self, source: ActionPairsCategory.ObjectType, target: ActionPairsCategory.ObjectType, arrow: MorphismCategory.ObjectType
    ) -> ActionPairsCategory.MorphismType: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...

class _StaticRoles_BimoduleCategory(sage_categories.cat.structured_objects._StaticRoles_EquifierCategory):
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def left_action(self) -> MorphismCategory.ObjectType: ...
        def right_action(self) -> MorphismCategory.ObjectType: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def domain(self) -> BimoduleCategory.ObjectType: ...
        def codomain(self) -> BimoduleCategory.ObjectType: ...

class BimoduleCategory(
    _StaticRoles_BimoduleCategory,
    EquifierCategory[_StaticRoles_BimoduleCategory.ObjectType, _StaticRoles_BimoduleCategory.ElementType, _StaticRoles_BimoduleCategory.MorphismType],
):
    def __init__(self, first: NaturalTransformation, second: NaturalTransformation, left: ModuleCategory, right: ModuleCategory, pairs: ActionPairsCategory) -> None: ...
    def left_modules(self) -> ModuleCategory: ...
    def right_modules(self) -> ModuleCategory: ...
    def monoidal_structure(self) -> MonoidalStructuresCategory.ObjectType: ...
    def underlying_category(self) -> Category: ...
    @cached_method
    def to_left(self) -> Functor: ...
    @cached_method
    def to_right(self) -> Functor: ...
    @cached_method
    def forgetful(self) -> Functor: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def __call__(self, left_action: MorphismCategory.ObjectType, right_action: MorphismCategory.ObjectType) -> BimoduleCategory.ObjectType: ...
    def homomorphism(self, source: BimoduleCategory.ObjectType, target: BimoduleCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> BimoduleCategory.MorphismType: ...

def Bimodules(left_scalars: MonoidCategory.ObjectType, right_scalars: MonoidCategory.ObjectType, monoidal: MonoidalStructuresCategory.ObjectType) -> BimoduleCategory: ...
