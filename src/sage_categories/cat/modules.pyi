from collections.abc import Callable

import sage_categories.cat.cat_constructions
import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from sage_categories.cat.calculus import pair_maps as pair_maps
from sage_categories.cat.cat_constructions import LimitSubcategory as LimitSubcategory
from sage_categories.cat.cat_constructions import (
    limit_of_categories as limit_of_categories,
)
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.choices import SelectedChoice as SelectedChoice
from sage_categories.cat.cones import cone as cone
from sage_categories.cat.cones import cones as cones
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.diagrams import from_sequence as from_sequence
from sage_categories.cat.diagrams import sequence_position as sequence_position
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.monoidal import ActionsCategory as ActionsCategory
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.shapes import Discrete as Discrete
from sage_categories.cat.structured_objects import (
    EndofunctorAlgebras as EndofunctorAlgebras,
)
from sage_categories.cat.structured_objects import Equifier as Equifier
from sage_categories.cat.structured_objects import EquifierCategory as EquifierCategory
from sage_categories.cat.structured_objects import InserterCategory as InserterCategory
from sage_categories.cat.structured_objects import MonoidCategory as MonoidCategory
from sage_categories.cat.structured_objects import Monoids as Monoids
from sage_categories.engines.presented_modules import tensor_morphism as tensor_morphism
from sage_categories.kernel.refinement import refine as refine
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function
from sage_categories.kernel.sage_runtime import cached_method as cached_method

__all__ = ["ModuleCategory", "Modules", "internal_endomorphism_module", "select_native_module_adapter"]

class _StaticRoles_ModuleCategory(sage_categories.cat.cat_constructions._StaticRoles_LimitSubcategory):
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def carrier(self) -> CategoryOfCategories.ElementType: ...
        def action(self) -> MorphismCategory.ObjectType: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def underlying_morphism(self) -> MorphismCategory.ObjectType: ...
        def domain(self) -> ModuleCategory.ObjectType: ...
        def codomain(self) -> ModuleCategory.ObjectType: ...

class ModuleCategory(
    _StaticRoles_ModuleCategory, LimitSubcategory[_StaticRoles_ModuleCategory.ObjectType, _StaticRoles_ModuleCategory.ElementType, _StaticRoles_ModuleCategory.MorphismType]
):
    def __init__(self, diagram: Functor, scalars: MonoidCategory.ObjectType, actegory: ActionsCategory.ObjectType, algebras: InserterCategory) -> None: ...
    def scalars(self) -> MonoidCategory.ObjectType: ...
    def actegory(self) -> ActionsCategory.ObjectType: ...
    def underlying_category(self) -> Category: ...
    def scalar_endofunctor(self) -> Functor: ...
    def carrier(self) -> CategoryOfCategories.ElementType: ...
    @cached_method
    def forgetful(self) -> Functor: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def __call__(self, action_morphism: MorphismCategory.ObjectType) -> ModuleCategory.ObjectType: ...
    def homomorphism(self, source: ModuleCategory.ObjectType, target: ModuleCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> ModuleCategory.MorphismType: ...
    def from_endomorphism_action(self, scalar_morphism: MorphismCategory.ObjectType) -> ModuleCategory.ObjectType: ...
    def from_sage_module(self, engine_module: object) -> ModuleCategory.ObjectType: ...
    def transport(self, module: ModuleCategory.ObjectType, isomorphism: MorphismCategory.ObjectType) -> ModuleCategory.ObjectType: ...
    def restriction(self, scalar_morphism: MorphismCategory.ObjectType) -> Functor: ...

type NativeModuleAdapter = Callable[[ModuleCategory, object], ModuleCategory.ObjectType]

def Modules(scalars: MonoidCategory.ObjectType, actegory: ActionsCategory.ObjectType) -> ModuleCategory: ...
def internal_endomorphism_module(
    endomorphisms: MonoidCategory.ObjectType, actegory: ActionsCategory.ObjectType, evaluation: MorphismCategory.ObjectType
) -> ModuleCategory.ObjectType: ...
def select_native_module_adapter(owner: Category, adapter: NativeModuleAdapter) -> None: ...
