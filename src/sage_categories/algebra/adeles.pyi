from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from sage_categories.algebra.local_fields import ExactLocalFieldPresentation, ExactLocalValue
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate
from sage_categories.geometry.spaces import TopologicalSpacesCategory
from sage_categories.geometry.topological_rings import TopologicalRingsCategory
from sage_categories.kernel.sage_runtime import cached_method
__all__ = ['AdeleValue', 'AdeleOpen', 'AdelePresentation', 'adeles_of_rationals']
IntegralityCertificate = Callable[[int], bool]
LocalComponentRule = Callable[[int], ExactLocalValue]
LocalCondition = Callable[[ExactLocalValue], bool | None]

@dataclass(frozen=True, eq=False, slots=True)
class AdeleValue:
    owner: object
    real: ExactLocalValue
    finite_component_rule: LocalComponentRule
    exceptional_primes: frozenset[int]
    integrality_certificate: IntegralityCertificate

    def finite_component(self, prime: int) -> ExactLocalValue:
        ...

    def component(self, place: str | int) -> ExactLocalValue:
        ...

    def certifies_integral_at(self, prime: int) -> bool:
        ...

    def __neg__(self) -> AdeleValue:
        ...

    def __add__(self, other: AdeleValue) -> AdeleValue:
        ...

    def __mul__(self, other: AdeleValue) -> AdeleValue:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class AdeleOpen:
    owner: object
    kind: str
    real_condition: LocalCondition | None
    finite_conditions: tuple[tuple[int, LocalCondition], ...]

    @property
    def exceptional_primes(self) -> frozenset[int]:
        ...

    def uses_integral_condition(self, prime: int) -> bool:
        ...

    def contains(self, value: AdeleValue) -> bool | None:
        ...

    def included_in(self, other: AdeleOpen) -> bool | None:
        ...

class _AdeleOpenIncludedPredicate(Predicate):
    name: str

@dataclass(frozen=True, eq=False, slots=True)
class AdelePresentation:
    owner: object
    ring: CategoryOfCategories.ElementType
    space: TopologicalSpacesCategory.ObjectType
    topological_ring: TopologicalRingsCategory.ObjectType
    rational_field: ExactLocalFieldPresentation
    real_field: ExactLocalFieldPresentation
    primes: CategoryOfCategories.ElementType
    empty_open: AdeleOpen
    whole_open: AdeleOpen

    def local_field(self, prime: int) -> ExactLocalFieldPresentation:
        ...

    def point(self, value: AdeleValue) -> CategoryOfCategories.ElementType:
        ...

    def value(self, real: ExactLocalValue, finite_components: LocalComponentRule, exceptional_primes: frozenset[int], integrality_certificate: IntegralityCertificate) -> AdeleValue:
        ...

    def zero_value(self) -> AdeleValue:
        ...

    def one_value(self) -> AdeleValue:
        ...

    def diagonal_value(self, value: Fraction | int) -> AdeleValue:
        ...

    @cached_method
    def component_map(self, place: str | int) -> MorphismCategory.ObjectType:
        ...

    @cached_method
    def diagonal_map(self) -> MorphismCategory.ObjectType:
        ...

    def basic_open(self, real_condition: LocalCondition, finite_conditions: dict[int, LocalCondition]) -> AdeleOpen:
        ...

    def open_object(self, open_set: AdeleOpen) -> CategoryOfCategories.ElementType:
        ...

def adeles_of_rationals() -> AdelePresentation:
    ...
