from collections.abc import Callable, Hashable
from dataclasses import dataclass
from sage.combinat.free_module import CombinatorialFreeModule
from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup_class
from sage.matrix.matrix_integer_dense import Matrix_integer_dense
from sage.modules.fg_pid.fgp_module import FGP_Module_class
from sage.structure.parent import Parent
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.monoidal import MonoidalStructuresCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import MonoidCategory
__all__ = ['Presentation', 'LinearForm', 'AbelianGroups', 'presented_abelian_group', 'integer_group', 'indexed_free_abelian_group', 'indexed_free_abelian_injection', 'indexed_free_abelian_mediator', 'indexed_free_abelian_coproduct', 'abelian_homomorphism', 'coequalizer_projection', 'coequalizer_mediator', 'bilinear_map', 'simple_tensor', 'tensor_mediator', 'AbelianTensor', 'relative_tensor', 'balanced_tensor', 'relative_tensor_mediator', 'induced_left_action', 'induced_right_action', 'relative_tensor_morphism', 'relative_left_unitor', 'relative_right_unitor', 'AbelianBimoduleTensor']
type Engine = AdditiveAbelianGroup_class | FGP_Module_class

@dataclass(frozen=True, eq=False, slots=True)
class Presentation:
    orders: tuple[int, ...]
    coordinates: Callable[[Hashable], tuple[int, ...]]
    element: Callable[[tuple[int, ...]], Hashable]
    factors: tuple[Presentation, ...] = ...

    def rank(self) -> int:
        ...

    def identity(self) -> LinearForm:
        ...

    def direct_sum(self, factors: tuple[Presentation, ...]) -> Presentation:
        ...

    def projection(self, index: int) -> LinearForm:
        ...

    def pair(self, components: tuple[LinearForm, ...], target: Presentation) -> LinearForm:
        ...

    def zero_datum(self) -> Hashable:
        ...

    def zero_map(self, source: Presentation) -> LinearForm:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class LinearForm:
    source: Presentation
    target: Presentation
    matrix: Matrix_integer_dense

    def evaluate(self, datum: Hashable) -> Hashable:
        ...

    def compose(self, first: LinearForm) -> LinearForm | None:
        ...

    def equals(self, other: LinearForm) -> bool | None:
        ...

    def reduced(self) -> Matrix_integer_dense:
        ...

    def inverse(self) -> LinearForm | None:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class _TensorData:
    first: CategoryOfCategories.ElementType
    second: CategoryOfCategories.ElementType
    quotient: FGP_Module_class

@dataclass(frozen=True, eq=False, slots=True)
class _IndexedTensorData:
    first: CategoryOfCategories.ElementType
    second: CategoryOfCategories.ElementType
    indexed_factor: CategoryOfCategories.ElementType
    rank_one_on_left: bool

@dataclass(frozen=True, eq=False, slots=True)
class _IndexedPairTensorData:
    first: CategoryOfCategories.ElementType
    second: CategoryOfCategories.ElementType

def AbelianGroups() -> Category:
    ...

def presented_abelian_group(engine: Engine) -> CategoryOfCategories.ElementType:
    ...

def integer_group() -> CategoryOfCategories.ElementType:
    ...

class _OwnedIndexFacade(Parent):

    def __init__(self, index_set: CategoryOfCategories.ElementType) -> None:
        ...

    def __contains__(self, datum: object) -> bool:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class _IndexedFreeAbelianData:
    index_set: CategoryOfCategories.ElementType
    engine: CombinatorialFreeModule

def indexed_free_abelian_group(index_set: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    ...

def indexed_free_abelian_injection(group: CategoryOfCategories.ElementType, index: Hashable) -> MorphismCategory.ObjectType:
    ...

def indexed_free_abelian_mediator(group: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, component: Callable[[Hashable], MorphismCategory.ObjectType]) -> MorphismCategory.ObjectType:
    ...

def indexed_free_abelian_coproduct(index_set: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    ...

def abelian_homomorphism(source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, rule: Callable[[Hashable], Hashable]) -> MorphismCategory.ObjectType:
    ...

def coequalizer_projection(first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def coequalizer_mediator(projection: MorphismCategory.ObjectType, coequalizing: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def bilinear_map(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
    ...

def simple_tensor(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType, left: Hashable, right: Hashable) -> CategoryOfCategories.ElementType:
    ...

def tensor_mediator(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, biadditive: Callable[[Hashable, Hashable], Hashable]) -> MorphismCategory.ObjectType:
    ...

def AbelianTensor() -> MonoidalStructuresCategory.ObjectType:
    ...

def relative_tensor(right_action: MorphismCategory.ObjectType, left_action: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def balanced_tensor(projection: MorphismCategory.ObjectType, left: Hashable, right: Hashable) -> CategoryOfCategories.ElementType:
    ...

def relative_tensor_mediator(projection: MorphismCategory.ObjectType, target: CategoryOfCategories.ElementType, balanced: Callable[[Hashable, Hashable], Hashable]) -> MorphismCategory.ObjectType:
    ...

def induced_left_action(projection: MorphismCategory.ObjectType, left_action: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def induced_right_action(projection: MorphismCategory.ObjectType, right_action: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def relative_tensor_morphism(source: MorphismCategory.ObjectType, target: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def relative_left_unitor(projection: MorphismCategory.ObjectType, left_action: MorphismCategory.ObjectType, unit_morphism: MorphismCategory.ObjectType) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    ...

def relative_right_unitor(projection: MorphismCategory.ObjectType, right_action: MorphismCategory.ObjectType, unit_morphism: MorphismCategory.ObjectType) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    ...

def AbelianBimoduleTensor(scalars: MonoidCategory.ObjectType) -> MonoidalStructuresCategory.ObjectType:
    ...

def _rule_abelian_homomorphism(source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, rule: Callable[[Hashable], Hashable]) -> MorphismCategory.ObjectType:
    ...

def _indexed_free_record(group: CategoryOfCategories.ElementType) -> _IndexedFreeAbelianData:
    ...

def presentation(group: CategoryOfCategories.ElementType) -> Presentation:
    ...

def _group_from_engine(engine: Engine) -> CategoryOfCategories.ElementType:
    ...

def _linear_homomorphism(source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, form: LinearForm) -> MorphismCategory.ObjectType:
    ...

def linear_form(arrow: MorphismCategory.ObjectType) -> LinearForm:
    ...

def _matrix_of_rows(rows: list, width: int) -> Matrix_integer_dense:
    ...
