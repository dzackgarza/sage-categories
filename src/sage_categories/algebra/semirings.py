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
from sage_categories.kernel.refinement import refine
from sage_categories.sets.category import Sets

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor


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
        return self.zero


class SemiringObjectDeclaration:
    """An object in ``Semirings(C)``."""

    def __init__(self, data: Any) -> None:
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


@dataclass(frozen=True, eq=False, slots=True)
class SemiringMorphismData:
    """A morphism in ``Semirings(C)``."""

    carrier_morphism: Any


class SemiringMorphismDeclaration:
    """A morphism in ``Semirings(C)``."""

    def __init__(self, data: SemiringMorphismData) -> None:
        self._carrier_morphism = data.carrier_morphism
        super().__init__()

    def carrier_morphism(self) -> Any:
        return self._carrier_morphism

    def __repr__(self) -> str:
        return f"SemiringMorphism({self.domain()!r} -> {self.codomain()!r})"


class SemiringsCategory(Category[[], []]):
    """``Semirings(C)``: strict internal semiring objects in a category ``C`` with finite products."""

    ObjectType = SemiringObjectDeclaration
    MorphismType = SemiringMorphismDeclaration

    class ElementType:
        """A generalized element of a semiring object."""

    def __init__(self, ambient: Category) -> None:
        self._ambient = ambient
        self._semirings: dict[Any, SemiringsCategory.ObjectType] = {}
        super().__init__()

    def ambient(self) -> Category:
        return self._ambient

    def additive_monoid_projection(self) -> Functor:
        """Projection to ``Monoids(C).Additive().Commutative()``."""
        target = Monoids(self._ambient).Additive().Commutative()

        def on_object(S: SemiringsCategory.ObjectType) -> Any:
            obj = Monoids(self._ambient)(S.carrier(), S.addition(), S.zero())
            refine(obj, target)
            return obj

        def on_morphism(f: SemiringsCategory.MorphismType) -> Any:
            mor = Monoids(self._ambient).construct_morphism(
                on_object(f.domain()),
                on_object(f.codomain()),
                f.carrier_morphism() if hasattr(f, "carrier_morphism") else f,
            )
            refine(mor, target.morphism_category(1))
            return mor

        return Fun(self, target).Monomorphisms().Isofibrations()(on_object, on_morphism)

    def multiplicative_monoid_projection(self) -> Functor:
        """Projection to ``Monoids(C).Multiplicative()``."""
        target = Monoids(self._ambient).Multiplicative()

        def on_object(S: SemiringsCategory.ObjectType) -> Any:
            obj = Monoids(self._ambient)(S.carrier(), S.multiplication(), S.one())
            refine(obj, target)
            return obj

        def on_morphism(f: SemiringsCategory.MorphismType) -> Any:
            mor = Monoids(self._ambient).construct_morphism(
                on_object(f.domain()),
                on_object(f.codomain()),
                f.carrier_morphism() if hasattr(f, "carrier_morphism") else f,
            )
            refine(mor, target.morphism_category(1))
            return mor

        return Fun(self, target).Monomorphisms().Isofibrations()(on_object, on_morphism)

    def product_projection(self, index: int) -> Functor:
        """Product projections: 0 is additive monoid projection, 1 is multiplicative monoid projection."""
        if index == 0:
            return self.additive_monoid_projection()
        if index == 1:
            return self.multiplicative_monoid_projection()
        raise IndexError(f"Semirings only has projections 0 and 1, got {index}")

    def structure_functors(self) -> tuple[Any, ...]:
        """Projections to the additive and multiplicative monoid categories."""
        return (
            self.additive_monoid_projection(),
            self.multiplicative_monoid_projection(),
        )

    def construct_morphism(
        self,
        domain: SemiringsCategory.ObjectType,
        codomain: SemiringsCategory.ObjectType,
        carrier_morphism: Any,
    ) -> SemiringsCategory.MorphismType:
        return self.MorphismType(
            self.morphism_category(1),
            domain,
            codomain,
            SemiringMorphismData(carrier_morphism),
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


def Semirings(ambient: Category | None = None) -> SemiringsCategory:
    """Construct or retrieve ``Semirings(ambient)``."""
    if ambient is None:
        ambient = Sets()
    if ambient not in _SEMIRING_CATEGORIES:
        _SEMIRING_CATEGORIES[ambient] = SemiringsCategory(ambient)
    return _SEMIRING_CATEGORIES[ambient]
