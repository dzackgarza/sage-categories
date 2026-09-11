from dataclasses import dataclass
from fractions import Fraction
from functools import cache

from sage_categories.algebra._certified_commutative_ring import certified_commutative_ring as certified_commutative_ring
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.structured_objects import Rings as Rings

__all__ = ["ExactLocalFieldPresentation", "ExactLocalValue", "exact_padic_field", "exact_rational_field", "exact_real_field", "prime_indices"]

@dataclass(frozen=True, slots=True)
class _ExactExpression:
    operation: str
    arguments: tuple[object, ...]

@dataclass(frozen=True, slots=True)
class ExactLocalValue:
    place: str | int
    expression: _ExactExpression

    @staticmethod
    def rational(place: str | int, value: Fraction | int) -> ExactLocalValue: ...
    @staticmethod
    def atom(place: str | int, name: object, valuation: int | None = None) -> ExactLocalValue: ...
    def rational_value(self) -> Fraction | None: ...
    def __neg__(self) -> ExactLocalValue: ...
    def __add__(self, other: ExactLocalValue) -> ExactLocalValue: ...
    def __mul__(self, other: ExactLocalValue) -> ExactLocalValue: ...
    def valuation(self) -> int | float | None: ...
    def is_integral(self) -> bool | None: ...

@dataclass(frozen=True, eq=False, slots=True)
class ExactLocalFieldPresentation:
    place: str | int
    ring: CategoryOfCategories.ElementType
    integers: CategoryOfCategories.ElementType | None

    def value(self, datum: Fraction | int) -> CategoryOfCategories.ElementType: ...
    def embed_rational(self, rational_ring: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType: ...

@cache
def exact_rational_field() -> ExactLocalFieldPresentation: ...
@cache
def exact_real_field() -> ExactLocalFieldPresentation: ...
@cache
def exact_padic_field(prime: int) -> ExactLocalFieldPresentation: ...
@cache
def prime_indices() -> CategoryOfCategories.ElementType: ...
