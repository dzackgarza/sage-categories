from _typeshed import Incomplete
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from sage_categories.algebra._certified_commutative_ring import certified_commutative_ring as certified_commutative_ring
from sage_categories.algebra.local_fields import ExactLocalFieldPresentation as ExactLocalFieldPresentation, ExactLocalValue as ExactLocalValue, exact_padic_field as exact_padic_field, exact_rational_field as exact_rational_field, exact_real_field as exact_real_field, prime_indices as prime_indices
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.morphisms import Mor as Mor, MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import Predicate as Predicate, Proposition as Proposition, register_handler as register_handler
from sage_categories.cat.shapes import Thin as Thin
from sage_categories.cat.structured_objects import Rings as Rings
from sage_categories.geometry.spaces import TopologicalSpaces as TopologicalSpaces, TopologicalSpacesCategory as TopologicalSpacesCategory
from sage_categories.geometry.topological_rings import BinaryContinuity as BinaryContinuity, ProductTopologyOpen as ProductTopologyOpen, TopologicalRings as TopologicalRings, TopologicalRingsCategory as TopologicalRingsCategory
from sage_categories.kernel.sage_runtime import cached_method as cached_method
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
    real_condition: LocalCondition
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

@dataclass(frozen=True, eq=False, slots=True)
class AdelePresentation:
    owner: object
    ring: CategoryOfCategories.ElementType
    space: TopologicalSpacesCategory.ObjectType[AdeleOpen]
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

@cache
def adeles_of_rationals() -> AdelePresentation:
    ...
