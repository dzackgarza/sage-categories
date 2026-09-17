from sage_categories.cat.cat_constructions import LimitSubcategory as LimitSubcategory, limit_of_categories as limit_of_categories
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.diagrams import cospan_diagram as cospan_diagram
from sage_categories.cat.functors import Cat as Cat, Fun as Fun, Functor as Functor, NaturalTransformation as NaturalTransformation
from sage_categories.cat.modules import ModuleCategory as ModuleCategory, Modules as Modules
from sage_categories.cat.monoidal import MonoidalStructuresCategory as MonoidalStructuresCategory, Reversed as Reversed, SelfAction as SelfAction, tensor_morphism as tensor_morphism
from sage_categories.cat.morphisms import Mor as Mor, MorphismCategory as MorphismCategory
from sage_categories.cat.structured_objects import EquifierCategory as EquifierCategory, MonoidCategory as MonoidCategory, Monoids as Monoids
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function, cached_method as cached_method

class ActionPairsCategory(LimitSubcategory):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

    @cached_method
    def to_left(self) -> Functor:
        ...

    @cached_method
    def to_right(self) -> Functor:
        ...

    def homomorphism(self, source: ActionPairsCategory.ObjectType, target: ActionPairsCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> ActionPairsCategory.MorphismType:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

class BimoduleCategory(EquifierCategory):

    class ObjectType:

        def left_action(self) -> MorphismCategory.ObjectType:
            ...

        def right_action(self) -> MorphismCategory.ObjectType:
            ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, first: NaturalTransformation, second: NaturalTransformation, left: ModuleCategory, right: ModuleCategory, pairs: ActionPairsCategory) -> None:
        ...

    def left_modules(self) -> ModuleCategory:
        ...

    def right_modules(self) -> ModuleCategory:
        ...

    def monoidal_structure(self) -> MonoidalStructuresCategory.ObjectType:
        ...

    def underlying_category(self) -> Category:
        ...

    @cached_method
    def to_left(self) -> Functor:
        ...

    @cached_method
    def to_right(self) -> Functor:
        ...

    @cached_method
    def forgetful(self) -> Functor:
        ...

    def __call__(self, left_action: MorphismCategory.ObjectType, right_action: MorphismCategory.ObjectType) -> BimoduleCategory.ObjectType:
        ...

    def homomorphism(self, source: BimoduleCategory.ObjectType, target: BimoduleCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> BimoduleCategory.MorphismType:
        ...

def Bimodules(left_scalars: MonoidCategory.ObjectType, right_scalars: MonoidCategory.ObjectType, monoidal: MonoidalStructuresCategory.ObjectType) -> BimoduleCategory:
    ...
