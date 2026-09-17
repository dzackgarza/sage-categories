from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from sage_categories.algebra._certified_commutative_ring import certified_commutative_ring as certified_commutative_ring
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.structured_objects import Rings as Rings

@dataclass(frozen=True, slots=True)
class ExactLocalValue:
    place: str | int

    @staticmethod
    def rational(place: str | int, value: Fraction | int) -> ExactLocalValue:
        ...

    @staticmethod
    def atom(place: str | int, name: object, valuation: int | None=None) -> ExactLocalValue:
        ...

    def rational_value(self) -> Fraction | None:
        ...

    def __neg__(self) -> ExactLocalValue:
        ...

    def __add__(self, other: ExactLocalValue) -> ExactLocalValue:
        ...

    def __mul__(self, other: ExactLocalValue) -> ExactLocalValue:
        ...

    def valuation(self) -> int | float | None:
        ...

    def is_integral(self) -> bool | None:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class NoIntegralSubring:
    place: str
type IntegralSubring = CategoryOfCategories.ElementType | NoIntegralSubring

@dataclass(frozen=True, eq=False, slots=True)
class ExactLocalFieldPresentation:
    place: str | int
    ring: CategoryOfCategories.ElementType
    integers: IntegralSubring

    def value(self, datum: Fraction | int) -> CategoryOfCategories.ElementType:
        ...

    def embed_rational(self, rational_ring: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

@cache
def exact_rational_field() -> ExactLocalFieldPresentation:
    ...

@cache
def exact_real_field() -> ExactLocalFieldPresentation:
    ...

@cache
def exact_padic_field(prime: int) -> ExactLocalFieldPresentation:
    ...

@cache
def prime_indices() -> CategoryOfCategories.ElementType:
    ...

@dataclass(frozen=True, slots=True)
class _ExactExpression:
    operation: str
    arguments: tuple[object, ...]
