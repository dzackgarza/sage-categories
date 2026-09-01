r"""``Semirings(C)``: strict internal semiring objects in a cartesian category (``specs/magmas-monoids-semirings.md``).

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

from collections.abc import Hashable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sage.rings.integer import Integer
from sage.structure.coerce_dict import MonoDict

from sage_categories.algebra.monoids import Monoids, MonoidsCategory
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.kernel.refinement import refine

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.cat.functors import Functor

# A private retention key: identity pairs ``(id(v), v)`` (POL-SAGE-013).
type Key = tuple[Hashable, ...]


@dataclass(frozen=True, eq=False)
class SemiringObjectData:
    """The carrier, additive monoid, and multiplicative monoid data of a semiring object."""

    carrier: CategoryOfCategories.ElementType
    addition: MorphismCategory.ObjectType
    zero: MorphismCategory.ObjectType | CategoryOfCategories.ElementType
    multiplication: MorphismCategory.ObjectType
    one: MorphismCategory.ObjectType | CategoryOfCategories.ElementType

    @property
    def unit(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        """The unit the compiled shared monoid occurrence reads: the additive unit (D56)."""
        return self.zero


class SemiringObjectDeclaration:
    """An object in ``Semirings(C)``."""

    def __init__(self, data: SemiringObjectData) -> None:
        self._carrier = data.carrier
        self._addition = data.addition
        self._zero = data.zero
        self._multiplication = data.multiplication
        self._one = data.one
        super().__init__()

    def carrier(self) -> CategoryOfCategories.ElementType:
        return self._carrier

    def addition(self) -> MorphismCategory.ObjectType:
        r"""``alpha: X \times X -> X``."""
        return self._addition

    def zero(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        """``zero: 1 -> X``."""
        return self._zero

    def multiplication(self) -> MorphismCategory.ObjectType:
        r"""``mu: X \times X -> X``."""
        return self._multiplication

    def one(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        """``one: 1 -> X``."""
        return self._one

    def __repr__(self) -> str:
        return f"Semiring({self._carrier!r})"


@dataclass(frozen=True, eq=False, slots=True)
class SemiringMorphismData:
    """A morphism in ``Semirings(C)``."""

    carrier_morphism: MorphismCategory.ObjectType


class SemiringMorphismDeclaration:
    """A morphism in ``Semirings(C)``."""

    def __init__(self, data: SemiringMorphismData) -> None:
        self._carrier_morphism = data.carrier_morphism
        super().__init__()

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
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
        self._semirings: dict[Key, SemiringsCategory.ObjectType] = {}
        super().__init__()

    def ambient(self) -> Category:
        return self._ambient

    def additive_monoid_projection(self) -> Functor:
        """Projection to ``Monoids(C).Additive().Commutative()``."""
        target = Monoids(self._ambient).Additive().Commutative()

        def on_object(S: SemiringsCategory.ObjectType) -> MonoidsCategory.ObjectType:
            obj = Monoids(self._ambient)(S.carrier(), S.addition(), S.zero())
            refine(obj, target)
            return obj

        def on_morphism(f: SemiringsCategory.MorphismType) -> MorphismCategory.ObjectType:
            mor = Monoids(self._ambient).construct_morphism(
                on_object(f.domain()),
                on_object(f.codomain()),
                f.carrier_morphism(),
            )
            refine(mor, target.morphism_category(1))
            return mor

        return Fun(self, target).Monomorphisms().Isofibrations()(on_object, on_morphism)

    def multiplicative_monoid_projection(self) -> Functor:
        """Projection to ``Monoids(C).Multiplicative()``."""
        target = Monoids(self._ambient).Multiplicative()

        def on_object(S: SemiringsCategory.ObjectType) -> MonoidsCategory.ObjectType:
            obj = Monoids(self._ambient)(S.carrier(), S.multiplication(), S.one())
            refine(obj, target)
            return obj

        def on_morphism(f: SemiringsCategory.MorphismType) -> MorphismCategory.ObjectType:
            mor = Monoids(self._ambient).construct_morphism(
                on_object(f.domain()),
                on_object(f.codomain()),
                f.carrier_morphism(),
            )
            refine(mor, target.morphism_category(1))
            return mor

        return Fun(self, target).Monomorphisms().Isofibrations()(on_object, on_morphism)

    def product_projection(self, index: int | Integer) -> Functor:
        """Product projections: 0 is additive monoid projection, 1 is multiplicative monoid projection."""
        if index == 0:
            return self.additive_monoid_projection()
        if index == 1:
            return self.multiplicative_monoid_projection()
        raise IndexError(f"Semirings only has projections 0 and 1, got {index}")

    def structure_functors(self) -> tuple[Functor, ...]:
        """Projections to the additive and multiplicative monoid categories."""
        return (
            self.additive_monoid_projection(),
            self.multiplicative_monoid_projection(),
        )

    def construct_morphism(
        self,
        domain: SemiringsCategory.ObjectType,
        codomain: SemiringsCategory.ObjectType,
        carrier_morphism: MorphismCategory.ObjectType,
    ) -> SemiringsCategory.MorphismType:
        return self.MorphismType(
            self.morphism_category(1),
            domain,
            codomain,
            SemiringMorphismData(carrier_morphism),
        )

    def __call__(
        self,
        carrier: CategoryOfCategories.ElementType,
        addition: MorphismCategory.ObjectType,
        zero: MorphismCategory.ObjectType | CategoryOfCategories.ElementType,
        multiplication: MorphismCategory.ObjectType,
        one: MorphismCategory.ObjectType | CategoryOfCategories.ElementType,
    ) -> SemiringsCategory.ObjectType:
        key = tuple((id(value), value) for value in (carrier, addition, zero, multiplication, one))
        if key not in self._semirings:
            self._semirings[key] = self.ObjectType(
                category=self,
                data=SemiringObjectData(carrier, addition, zero, multiplication, one),
            )
        return self._semirings[key]

    def __repr__(self) -> str:
        return f"Semirings({self._ambient!r})"


_SEMIRING_CATEGORIES: MonoDict = MonoDict()


def Semirings(ambient: Category) -> SemiringsCategory:
    """Construct or retrieve ``Semirings(ambient)``, one category per ambient value."""
    if ambient not in _SEMIRING_CATEGORIES:
        _SEMIRING_CATEGORIES[ambient] = SemiringsCategory(ambient)
    return _SEMIRING_CATEGORIES[ambient]
