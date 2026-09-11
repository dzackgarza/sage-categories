import sage_categories.cat.structured_objects
import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.monoidal import ActionsCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import EquifierCategory, InserterCategory, MonoidCategory
from sage_categories.kernel.sage_runtime import cached_method
__all__ = ['ModuleCategory', 'Modules']

class _StaticRoles_ModuleCategory(sage_categories.cat.structured_objects._StaticRoles_EquifierCategory):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def action(self) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> ModuleCategory.ObjectType:
            ...

        def codomain(self) -> ModuleCategory.ObjectType:
            ...

class ModuleCategory(_StaticRoles_ModuleCategory, EquifierCategory[_StaticRoles_ModuleCategory.ObjectType, _StaticRoles_ModuleCategory.ElementType, _StaticRoles_ModuleCategory.MorphismType]):

    def __init__(self, first: NaturalTransformation, second: NaturalTransformation, scalars: MonoidCategory.ObjectType, actegory: ActionsCategory.ObjectType, algebras: InserterCategory) -> None:
        ...

    def scalars(self) -> MonoidCategory.ObjectType:
        ...

    def actegory(self) -> ActionsCategory.ObjectType:
        ...

    def underlying_category(self) -> Category:
        ...

    def scalar_endofunctor(self) -> Functor:
        ...

    def carrier(self) -> CategoryOfCategories.ElementType:
        ...

    @cached_method
    def forgetful(self) -> Functor:
        ...

    def __call__(self, action_morphism: MorphismCategory.ObjectType) -> ModuleCategory.ObjectType:
        ...

    def homomorphism(self, source: ModuleCategory.ObjectType, target: ModuleCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> ModuleCategory.MorphismType:
        ...

    def transport(self, module: ModuleCategory.ObjectType, isomorphism: MorphismCategory.ObjectType) -> ModuleCategory.ObjectType:
        ...

    def restriction(self, scalar_morphism: MorphismCategory.ObjectType) -> Functor:
        ...

def Modules(scalars: MonoidCategory.ObjectType, actegory: ActionsCategory.ObjectType) -> ModuleCategory:
    ...
