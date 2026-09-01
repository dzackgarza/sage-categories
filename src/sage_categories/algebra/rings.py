r"""``Rings(C)``: internal ring objects in a cartesian category (``specs/rings.md``).

An object of ``Rings(C)`` is an object ``R`` in ``C`` equipped with:
- addition ``+: R \times R -> R``
- multiplication ``\cdot: R \times R -> R``
- zero ``0: 1 -> R``
- one ``1: 1 -> R``
- additive inversion ``-: R -> R``

These make ``(R, +, 0, -)`` an object of ``Groups(C).Additive().Commutative()``,
and ``(R, +, 0, \cdot, 1)`` an object of ``Semirings(C)``.

The defining category is their pullback:
``Rings(C) = Semirings(C) \times_A Groups(C).Additive().Commutative()``
where ``A = Monoids(C).Additive().Commutative()``.

The structure functors are both projections:
``Rings(C).product_projection(0)`` and ``Rings(C).product_projection(1)``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sage_categories.algebra.groups import Groups
from sage_categories.algebra.semirings import Semirings
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.refinement import refine
from sage_categories.sets.category import Sets

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor


@dataclass(frozen=True, eq=False)
class RingObjectData:
    """The carrier, addition, zero, multiplication, one, and additive inversion data."""

    carrier: Any
    addition: Any
    zero: Any
    multiplication: Any
    one: Any
    inversion: Any

    @property
    def unit(self) -> Any:
        return self.zero


class RingObjectDeclaration:
    """An object in ``Rings(C)``."""

    def __init__(self, data: Any) -> None:
        self._carrier = data.carrier
        self._addition = getattr(data, "addition", getattr(data, "multiplication", None))
        self._zero = getattr(data, "zero", getattr(data, "unit", None))
        self._multiplication = getattr(data, "multiplication", None)
        self._one = getattr(data, "one", None)
        self._inversion = getattr(data, "inversion", None)
        super().__init__()

    def carrier(self) -> Any:
        return self._carrier

    def addition(self) -> Any:
        return self._addition

    def zero(self) -> Any:
        return self._zero

    def multiplication(self) -> Any:
        return self._multiplication

    def one(self) -> Any:
        return self._one

    def inversion(self) -> Any:
        """Additive inversion ``-: R -> R``."""
        return self._inversion

    def __repr__(self) -> str:
        return f"Ring({self._carrier!r})"


@dataclass(frozen=True, eq=False, slots=True)
class RingMorphismData:
    """A morphism in ``Rings(C)``."""

    carrier_morphism: Any


class RingMorphismDeclaration:
    """A morphism in ``Rings(C)``."""

    def __init__(self, data: RingMorphismData) -> None:
        self._carrier_morphism = data.carrier_morphism
        super().__init__()

    def carrier_morphism(self) -> Any:
        return self._carrier_morphism

    def __repr__(self) -> str:
        return f"RingMorphism({self.domain()!r} -> {self.codomain()!r})"


class RingsCategory(Category[[], []]):
    """``Rings(C)``: internal ring objects in a category ``C`` with finite products."""

    ObjectType = RingObjectDeclaration
    MorphismType = RingMorphismDeclaration

    class ElementType:
        """A generalized element of a ring object."""

    def __init__(self, ambient: Category) -> None:
        self._ambient = ambient
        self._rings: dict[Any, RingsCategory.ObjectType] = {}
        super().__init__()
        self._commutative = PropertySubcategory(self, "Commutative", ())

    def ambient(self) -> Category:
        return self._ambient

    def Commutative(self) -> PropertySubcategory:
        return self._commutative

    def semiring_projection(self) -> Functor:
        """Projection to ``Semirings(C)``."""
        target = Semirings(self._ambient)

        def on_object(R: RingsCategory.ObjectType) -> Any:
            return target(R.carrier(), R.addition(), R.zero(), R.multiplication(), R.one())

        def on_morphism(f: RingsCategory.MorphismType) -> Any:
            return target.construct_morphism(
                on_object(f.domain()),
                on_object(f.codomain()),
                f.carrier_morphism() if hasattr(f, "carrier_morphism") else f,
            )

        return Fun(self, target).Monomorphisms().Isofibrations()(on_object, on_morphism)

    def additive_group_projection(self) -> Functor:
        """Projection to ``Groups(C).Additive().Commutative()``."""
        target = Groups(self._ambient).Additive().Commutative()

        def on_object(R: RingsCategory.ObjectType) -> Any:
            obj = Groups(self._ambient)(R.carrier(), R.addition(), R.zero(), R.inversion())
            refine(obj, target)
            return obj

        def on_morphism(f: RingsCategory.MorphismType) -> Any:
            mor = Groups(self._ambient).construct_morphism(
                on_object(f.domain()),
                on_object(f.codomain()),
                f.carrier_morphism() if hasattr(f, "carrier_morphism") else f,
            )
            refine(mor, target.morphism_category(1))
            return mor

        return Fun(self, target).Monomorphisms().Isofibrations()(on_object, on_morphism)

    def product_projection(self, index: int) -> Functor:
        """Pullback projections: 0 is semiring projection, 1 is additive group projection."""
        if index == 0:
            return self.semiring_projection()
        if index == 1:
            return self.additive_group_projection()
        raise IndexError(f"Rings only has pullback projections 0 and 1, got {index}")

    def structure_functors(self) -> tuple[Any, ...]:
        """The two pullback projections: (self.product_projection(0), self.product_projection(1))."""
        return (
            self.product_projection(0),
            self.product_projection(1),
        )

    def construct_morphism(
        self,
        domain: RingsCategory.ObjectType,
        codomain: RingsCategory.ObjectType,
        carrier_morphism: Any,
    ) -> RingsCategory.MorphismType:
        return self.MorphismType(
            self.morphism_category(1),
            domain,
            codomain,
            RingMorphismData(carrier_morphism),
        )

    def __call__(
        self,
        carrier: Any,
        addition: Any,
        zero: Any,
        multiplication: Any,
        one: Any,
        inversion: Any,
    ) -> RingsCategory.ObjectType:
        key = (carrier, addition, zero, multiplication, one, inversion)
        if key not in self._rings:
            self._rings[key] = self.ObjectType(
                category=self,
                data=RingObjectData(carrier, addition, zero, multiplication, one, inversion),
            )
        return self._rings[key]

    def __repr__(self) -> str:
        return f"Rings({self._ambient!r})"


_RING_CATEGORIES: dict[Category, RingsCategory] = {}


def Rings(ambient: Category | None = None) -> RingsCategory:
    """Construct or retrieve ``Rings(ambient)``."""
    if ambient is None:
        ambient = Sets()
    if ambient not in _RING_CATEGORIES:
        _RING_CATEGORIES[ambient] = RingsCategory(ambient)
    return _RING_CATEGORIES[ambient]
