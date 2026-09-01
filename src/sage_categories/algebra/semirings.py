"""``Semirings(C)``: strict internal semiring objects in a cartesian category (``specs/magmas-monoids-semirings.md``).

A strict internal semiring object in ``C`` consists of an object ``X`` in ``C`` with:
- a commutative additive monoid structure on ``X`` (``alpha: X \times X -> X``, ``zero: 1 -> X``)
- a multiplicative monoid structure on ``X`` (``mu: X \times X -> X``, ``one: 1 -> X``)
- left and right distributivity diagrams
- left and right zero-absorption diagrams.

At ``C = Cat()``, an object is a category ``X`` whose addition and multiplication are
functors ``X \times X -> X``, and whose laws are equalities of functors.  ``Cardinal()``
is the canonical object of ``Semirings(Cat())``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sage_categories.algebra.monoids import Monoids
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun


@dataclass(frozen=True, eq=False)
class SemiringObjectData:
    """The carrier, additive monoid, and multiplicative monoid data of a semiring object."""

    carrier: Any
    addition: Any
    zero: Any
    multiplication: Any
    one: Any

    @property
    def unit(self) -> Any:
        return self.one


class SemiringObjectDeclaration:
    """An object in ``Semirings(C)``."""

    def __init__(self, data: SemiringObjectData) -> None:
        self._carrier = data.carrier
        self._addition = data.addition
        self._zero = data.zero
        self._multiplication = data.multiplication
        self._one = data.one
        super().__init__()

    def carrier(self) -> Any:
        return self._carrier

    def addition(self) -> Any:
        """``alpha: X \times X -> X``."""
        return self._addition

    def zero(self) -> Any:
        """``zero: 1 -> X``."""
        return self._zero

    def multiplication(self) -> Any:
        """``mu: X \times X -> X``."""
        return self._multiplication

    def one(self) -> Any:
        """``one: 1 -> X``."""
        return self._one

    def __repr__(self) -> str:
        return f"Semiring({self._carrier!r})"


class SemiringsCategory(Category[[], []]):
    """``Semirings(C)``: strict internal semiring objects in a category ``C`` with finite products."""

    ObjectType = SemiringObjectDeclaration

    class ElementType:
        """A generalized element of a semiring object."""

    class MorphismType:
        """A morphism of semirings."""

    def __init__(self, ambient: Category) -> None:
        self._ambient = ambient
        self._semirings: dict[Any, SemiringsCategory.ObjectType] = {}
        super().__init__()

    def ambient(self) -> Category:
        return self._ambient

    def structure_functors(self) -> tuple[Any, ...]:
        """Projections to the additive and multiplicative monoid categories."""
        monoids = Monoids(self._ambient)
        add_monoids = monoids.Additive()
        mul_monoids = monoids.Multiplicative()
        return (
            Fun(self, add_monoids).Monomorphisms().Isofibrations()(),
            Fun(self, mul_monoids).Monomorphisms().Isofibrations()(),
        )

    def __call__(
        self,
        carrier: Any,
        addition: Any,
        zero: Any,
        multiplication: Any,
        one: Any,
    ) -> SemiringsCategory.ObjectType:
        key = (carrier, addition, zero, multiplication, one)
        if key not in self._semirings:
            self._semirings[key] = self.ObjectType(
                category=self,
                data=SemiringObjectData(carrier, addition, zero, multiplication, one),
            )
        return self._semirings[key]

    def __repr__(self) -> str:
        return f"Semirings({self._ambient!r})"


_SEMIRING_CATEGORIES: dict[Category, SemiringsCategory] = {}


def Semirings(ambient: Category) -> SemiringsCategory:
    """Construct or retrieve ``Semirings(ambient)``."""
    if ambient not in _SEMIRING_CATEGORIES:
        _SEMIRING_CATEGORIES[ambient] = SemiringsCategory(ambient)
    return _SEMIRING_CATEGORIES[ambient]
