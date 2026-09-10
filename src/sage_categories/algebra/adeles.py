"""The exact adelic restricted product of ``QQ`` over all places."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, cast

from sympy import false, true
from sympy.ntheory import factorint
from sympy.ntheory.primetest import isprime

from sage_categories.algebra._certified_commutative_ring import (
    certified_commutative_ring,
)
from sage_categories.algebra.local_fields import (
    ExactLocalFieldPresentation,
    ExactLocalValue,
    exact_padic_field,
    exact_rational_field,
    exact_real_field,
    prime_indices,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition, register_handler
from sage_categories.cat.shapes import Thin
from sage_categories.cat.structured_objects import Rings
from sage_categories.geometry.spaces import TopologicalSpaces, TopologicalSpacesCategory
from sage_categories.geometry.topological_rings import (
    BinaryContinuity,
    ProductTopologyOpen,
    TopologicalRings,
    TopologicalRingsCategory,
)
from sage_categories.kernel.sage_runtime import cached_method

__all__ = [
    "AdeleOpen",
    "AdelePresentation",
    "AdeleValue",
    "adeles_of_rationals",
]


IntegralityCertificate = Callable[[int], bool]
LocalComponentRule = Callable[[int], ExactLocalValue]
LocalCondition = Callable[[ExactLocalValue], bool | None]


@dataclass(frozen=True, eq=False, slots=True)
class AdeleValue:
    """One exact adele with all finite components retained by a callable rule."""

    owner: object
    real: ExactLocalValue
    finite_component_rule: LocalComponentRule
    exceptional_primes: frozenset[int]
    integrality_certificate: IntegralityCertificate

    def finite_component(self, prime: int) -> ExactLocalValue:
        assert isprime(prime)
        value = self.finite_component_rule(prime)
        assert value.place == prime
        return value

    def component(self, place: str | int) -> ExactLocalValue:
        match place:
            case "real":
                return self.real
            case int():
                return self.finite_component(place)
            case _:
                raise AssertionError(f"unknown adele place {place!r}")

    def certifies_integral_at(self, prime: int) -> bool:
        assert isprime(prime)
        match prime in self.exceptional_primes:
            case True:
                return self.finite_component(prime).is_integral() is True
            case False:
                return self.integrality_certificate(prime)

    def __neg__(self) -> AdeleValue:
        return AdeleValue(
            self.owner,
            -self.real,
            lambda prime: -self.finite_component(prime),
            self.exceptional_primes,
            self.integrality_certificate,
        )

    def __add__(self, other: AdeleValue) -> AdeleValue:
        assert self.owner is other.owner
        exceptional = self.exceptional_primes | other.exceptional_primes
        return AdeleValue(
            self.owner,
            self.real + other.real,
            lambda prime: self.finite_component(prime) + other.finite_component(prime),
            exceptional,
            lambda prime: (
                self.integrality_certificate(prime)
                and other.integrality_certificate(prime)
            ),
        )

    def __mul__(self, other: AdeleValue) -> AdeleValue:
        assert self.owner is other.owner
        exceptional = self.exceptional_primes | other.exceptional_primes
        return AdeleValue(
            self.owner,
            self.real * other.real,
            lambda prime: self.finite_component(prime) * other.finite_component(prime),
            exceptional,
            lambda prime: (
                self.integrality_certificate(prime)
                and other.integrality_certificate(prime)
            ),
        )


@dataclass(frozen=True, eq=False, slots=True)
class AdeleOpen:
    """A certified open of the restricted-product topology."""

    owner: object
    kind: str
    real_condition: LocalCondition | None
    finite_conditions: tuple[tuple[int, LocalCondition], ...]

    @property
    def exceptional_primes(self) -> frozenset[int]:
        return frozenset(prime for prime, _ in self.finite_conditions)

    def uses_integral_condition(self, prime: int) -> bool:
        assert isprime(prime)
        return prime not in self.exceptional_primes

    def contains(self, value: AdeleValue) -> bool | None:
        assert value.owner is self.owner
        match self.kind:
            case "whole":
                return True
            case "empty":
                return False
            case "basic":
                pass
            case _:
                return None
        match value.exceptional_primes <= self.exceptional_primes:
            case False:
                return False
            case True:
                pass
        assert self.real_condition is not None
        real_answer = self.real_condition(value.real)
        match real_answer:
            case False:
                return False
            case _:
                pass
        answers = tuple(
            condition(value.finite_component(prime))
            for prime, condition in self.finite_conditions
        )
        match any(answer is False for answer in answers):
            case True:
                return False
            case False:
                pass
        match real_answer is True and all(answer is True for answer in answers):
            case True:
                return True
            case False:
                return None

    def included_in(self, other: AdeleOpen) -> bool | None:
        assert self.owner is other.owner
        match self is other:
            case True:
                return True
            case False:
                pass
        match self.kind, other.kind:
            case "empty", _:
                return True
            case _, "whole":
                return True
            case _:
                return None


class _AdeleOpenIncludedPredicate(Predicate):
    name = "adele_open_included"


adele_open_included = _AdeleOpenIncludedPredicate()


def _open_inclusion_handler(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
) -> bool | None:
    left, right = cast(Any, first).datum(), cast(Any, second).datum()
    match left, right:
        case AdeleOpen(), AdeleOpen():
            return left.included_in(right)
        case _:
            return None


register_handler(adele_open_included, _open_inclusion_handler)


def _open_order(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
) -> Proposition:
    return adele_open_included(first, second)


@dataclass(frozen=True, eq=False, slots=True)
class AdelePresentation:
    """The exact topological ring ``A_Q = R x product'_p Q_p``."""

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
        return exact_padic_field(prime)

    def point(self, value: AdeleValue) -> CategoryOfCategories.ElementType:
        assert value.owner is self.owner
        return cast(
            CategoryOfCategories.ElementType,
            cast(Any, Rings(Sets).forgetful().on_object(self.ring)).point(value),
        )

    def value(
        self,
        real: ExactLocalValue,
        finite_components: LocalComponentRule,
        exceptional_primes: frozenset[int],
        integrality_certificate: IntegralityCertificate,
    ) -> AdeleValue:
        assert real.place == "real"
        assert all(isprime(prime) for prime in exceptional_primes)
        return AdeleValue(
            self.owner,
            real,
            finite_components,
            exceptional_primes,
            integrality_certificate,
        )

    def zero_value(self) -> AdeleValue:
        return self.value(
            ExactLocalValue.rational("real", 0),
            lambda prime: ExactLocalValue.rational(prime, 0),
            frozenset(),
            lambda _: True,
        )

    def one_value(self) -> AdeleValue:
        return self.value(
            ExactLocalValue.rational("real", 1),
            lambda prime: ExactLocalValue.rational(prime, 1),
            frozenset(),
            lambda _: True,
        )

    def diagonal_value(self, value: Fraction | int) -> AdeleValue:
        rational = Fraction(value)
        exceptions = frozenset(int(prime) for prime in factorint(rational.denominator))
        return self.value(
            ExactLocalValue.rational("real", rational),
            lambda prime: ExactLocalValue.rational(prime, rational),
            exceptions,
            lambda prime: prime not in exceptions,
        )

    @cached_method
    def component_map(self, place: str | int) -> MorphismCategory.ObjectType:
        rings = Rings(Sets)
        source_carrier = rings.forgetful().on_object(self.ring)
        match place:
            case "real":
                target = self.real_field
            case int():
                target = self.local_field(place)
            case _:
                raise AssertionError(f"unknown adele place {place!r}")
        target_carrier = rings.forgetful().on_object(target.ring)
        carrier_map = Mor(Sets)(source_carrier, target_carrier)(
            lambda value: cast(AdeleValue, value).component(place)
        )
        return rings.homomorphism(self.ring, target.ring, carrier_map)

    @cached_method
    def diagonal_map(self) -> MorphismCategory.ObjectType:
        rings = Rings(Sets)
        source = self.rational_field.ring
        source_carrier = rings.forgetful().on_object(source)
        target_carrier = rings.forgetful().on_object(self.ring)

        def diagonal(value: ExactLocalValue) -> AdeleValue:
            rational = value.rational_value()
            assert rational is not None
            return self.diagonal_value(rational)

        carrier_map = Mor(Sets)(source_carrier, target_carrier)(diagonal)
        return rings.homomorphism(source, self.ring, carrier_map)

    def basic_open(
        self,
        real_condition: LocalCondition,
        finite_conditions: dict[int, LocalCondition],
    ) -> AdeleOpen:
        assert all(isprime(prime) for prime in finite_conditions)
        return AdeleOpen(
            self.owner,
            "basic",
            real_condition,
            tuple(sorted(finite_conditions.items(), key=lambda item: item[0])),
        )

    def open_object(self, open_set: AdeleOpen) -> CategoryOfCategories.ElementType:
        assert open_set.owner is self.owner
        return self.space.open_object(open_set)


_adeles: AdelePresentation | None = None


def adeles_of_rationals() -> AdelePresentation:
    """Return the exact restricted product ``R x product'_p Q_p`` relative to ``Z_p``."""
    global _adeles
    match _adeles:
        case AdelePresentation():
            return _adeles
        case None:
            pass

    owner = object()
    carrier = Sets.from_membership(
        lambda value: (
            true if isinstance(value, AdeleValue) and value.owner is owner else false
        )
    )
    zero = AdeleValue(
        owner,
        ExactLocalValue.rational("real", 0),
        lambda prime: ExactLocalValue.rational(prime, 0),
        frozenset(),
        lambda _: True,
    )
    one = AdeleValue(
        owner,
        ExactLocalValue.rational("real", 1),
        lambda prime: ExactLocalValue.rational(prime, 1),
        frozenset(),
        lambda _: True,
    )
    ring = certified_commutative_ring(
        carrier,
        lambda pair: cast(AdeleValue, pair[0]) + cast(AdeleValue, pair[1]),
        lambda pair: cast(AdeleValue, pair[0]) * cast(AdeleValue, pair[1]),
        zero,
        one,
    )

    opens = Sets.from_membership(
        lambda value: (
            true if isinstance(value, AdeleOpen) and value.owner is owner else false
        )
    )
    open_category = Thin(opens, _open_order)

    def open_point(key: object) -> CategoryOfCategories.ElementType:
        assert isinstance(key, AdeleOpen) and key.owner is owner
        return cast(CategoryOfCategories.ElementType, cast(Any, opens).point(key))

    space = TopologicalSpaces().from_open_category(
        carrier,
        opens,
        open_category,
        open_point,
        lambda key: open_category(open_point(key)),
    )
    addition = cast(MorphismCategory.ObjectType, cast(Any, ring).addition())
    multiplication = cast(MorphismCategory.ObjectType, cast(Any, ring).multiplication())

    def binary_preimage(
        operation: str,
        open_object: CategoryOfCategories.ElementType,
    ) -> ProductTopologyOpen:
        open_set = cast(AdeleOpen, cast(Any, open_object).point().datum())

        def membership(pair: tuple[object, object]) -> bool | None:
            first, second = cast(AdeleValue, pair[0]), cast(AdeleValue, pair[1])
            match operation:
                case "addition":
                    return open_set.contains(first + second)
                case "multiplication":
                    return open_set.contains(first * second)

        return ProductTopologyOpen(
            space,
            membership,
            ("restricted-product-preimage", operation, open_set),
        )

    addition_continuity = BinaryContinuity(
        space,
        addition,
        lambda open_object: binary_preimage("addition", open_object),
    )
    multiplication_continuity = BinaryContinuity(
        space,
        multiplication,
        lambda open_object: binary_preimage("multiplication", open_object),
    )
    topological_ring = TopologicalRings()(
        ring,
        space,
        addition_continuity,
        multiplication_continuity,
    )
    empty_open = AdeleOpen(owner, "empty", None, ())
    whole_open = AdeleOpen(owner, "whole", None, ())
    _adeles = AdelePresentation(
        owner,
        ring,
        space,
        topological_ring,
        exact_rational_field(),
        exact_real_field(),
        prime_indices(),
        empty_open,
        whole_open,
    )
    return _adeles
