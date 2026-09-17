import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.cat.structured_objects
import sage_categories.kernel.roles
from sage_categories.cat.calculus import pair_maps as pair_maps
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.monoidal import ActionsCategory as ActionsCategory
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
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

__all__ = ["ModuleCategory", "Modules"]

class _StaticRoles_ModuleCategory(sage_categories.cat.structured_objects._StaticRoles_EquifierCategory):
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def action(self) -> MorphismCategory.ObjectType: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def domain(self) -> ModuleCategory.ObjectType: ...
        def codomain(self) -> ModuleCategory.ObjectType: ...

class ModuleCategory(
    _StaticRoles_ModuleCategory, EquifierCategory[_StaticRoles_ModuleCategory.ObjectType, _StaticRoles_ModuleCategory.ElementType, _StaticRoles_ModuleCategory.MorphismType]
):
    def __init__(
        self, first: NaturalTransformation, second: NaturalTransformation, scalars: MonoidCategory.ObjectType, actegory: ActionsCategory.ObjectType, algebras: InserterCategory
    ) -> None: ...
    def scalars(self) -> MonoidCategory.ObjectType: ...
    def actegory(self) -> ActionsCategory.ObjectType: ...
    def underlying_category(self) -> Category: ...
    def scalar_endofunctor(self) -> Functor: ...
    def carrier(self) -> CategoryOfCategories.ElementType: ...
    @cached_method
    def forgetful(self) -> Functor: ...
    def __call__(self, action_morphism: MorphismCategory.ObjectType) -> ModuleCategory.ObjectType: ...
    def homomorphism(self, source: ModuleCategory.ObjectType, target: ModuleCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> ModuleCategory.MorphismType: ...
    def transport(self, module: ModuleCategory.ObjectType, isomorphism: MorphismCategory.ObjectType) -> ModuleCategory.ObjectType: ...
    def restriction(self, scalar_morphism: MorphismCategory.ObjectType) -> Functor: ...

def Modules(scalars: MonoidCategory.ObjectType, actegory: ActionsCategory.ObjectType) -> ModuleCategory: ...
