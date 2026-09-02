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

from collections.abc import Hashable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sage.misc.cachefunc import cached_method
from sage.rings.integer import Integer
from sage.structure.coerce_dict import MonoDict

from sage_categories.algebra.groups import Groups, GroupsCategory
from sage_categories.algebra.semirings import Semirings, SemiringsCategory
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.refinement import refine

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.cat.functors import Functor

# A private retention key: identity pairs ``(id(v), v)`` (POL-SAGE-013).
type Key = tuple[Hashable, ...]


@dataclass(frozen=True, eq=False)
class RingObjectData:
    """The carrier, addition, zero, multiplication, one, and additive inversion data."""

    carrier: CategoryOfCategories.ElementType
    addition: MorphismCategory.ObjectType
    zero: MorphismCategory.ObjectType | CategoryOfCategories.ElementType
    multiplication: MorphismCategory.ObjectType
    one: MorphismCategory.ObjectType | CategoryOfCategories.ElementType
    inversion: MorphismCategory.ObjectType

    @property
    def unit(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        """The unit the compiled shared monoid occurrence reads: the additive unit (D56)."""
        return self.zero


class RingObjectDeclaration:
    """An object in ``Rings(C)``."""

    def __init__(self, data: RingObjectData) -> None:
        self._carrier = data.carrier
        self._addition = data.addition
        self._zero = data.zero
        self._multiplication = data.multiplication
        self._one = data.one
        self._inversion = data.inversion

    def carrier(self) -> CategoryOfCategories.ElementType:
        return self._carrier

    def addition(self) -> MorphismCategory.ObjectType:
        return self._addition

    def zero(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        return self._zero

    def multiplication(self) -> MorphismCategory.ObjectType:
        return self._multiplication

    def one(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        return self._one

    def inversion(self) -> MorphismCategory.ObjectType:
        """Additive inversion ``-: R -> R``."""
        return self._inversion

    def __repr__(self) -> str:
        return f"Ring({self._carrier!r})"


@dataclass(frozen=True, eq=False, slots=True)
class RingMorphismData:
    """A morphism in ``Rings(C)``."""

    carrier_morphism: MorphismCategory.ObjectType


class RingMorphismDeclaration:
    """A morphism in ``Rings(C)``."""

    def __init__(self, data: RingMorphismData) -> None:
        self._carrier_morphism = data.carrier_morphism

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
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
        self._rings: dict[Key, RingsCategory.ObjectType] = {}
        super().__init__()
        self._commutative = PropertySubcategory(self, "Commutative", ())

    def ambient(self) -> Category:
        return self._ambient

    def Commutative(self) -> PropertySubcategory:
        return self._commutative

    @cached_method
    def semiring_projection(self) -> Functor:
        """Projection to ``Semirings(C)``, retained once."""
        target = Semirings(self._ambient)

        def on_object(R: RingsCategory.ObjectType) -> SemiringsCategory.ObjectType:
            return target(R.carrier(), R.addition(), R.zero(), R.multiplication(), R.one())

        def on_morphism(f: RingsCategory.MorphismType) -> MorphismCategory.ObjectType:
            return target.construct_morphism(
                on_object(f.domain()),
                on_object(f.codomain()),
                f.carrier_morphism(),
            )

        return Fun(self, target).Monomorphisms().Isofibrations()(on_object, on_morphism)

    @cached_method
    def additive_group_projection(self) -> Functor:
        """Projection to ``Groups(C).Additive().Commutative()``, retained once."""
        target = Groups(self._ambient).Additive().Commutative()

        def on_object(R: RingsCategory.ObjectType) -> GroupsCategory.ObjectType:
            obj = Groups(self._ambient)(R.carrier(), R.addition(), R.zero(), R.inversion())
            refine(obj, target)
            return obj

        def on_morphism(f: RingsCategory.MorphismType) -> MorphismCategory.ObjectType:
            mor = Groups(self._ambient).construct_morphism(
                on_object(f.domain()),
                on_object(f.codomain()),
                f.carrier_morphism(),
            )
            refine(mor, target.morphism_category(1))
            return mor

        return Fun(self, target).Monomorphisms().Isofibrations()(on_object, on_morphism)

    def product_projection(self, index: int | Integer) -> Functor:
        """Pullback projections: 0 is semiring projection, 1 is additive group projection."""
        if index == 0:
            return self.semiring_projection()
        if index == 1:
            return self.additive_group_projection()
        raise IndexError(f"Rings only has pullback projections 0 and 1, got {index}")

    def structure_functors(self) -> tuple[Functor, ...]:
        """The two pullback projections: (self.product_projection(0), self.product_projection(1))."""
        return (
            self.product_projection(0),
            self.product_projection(1),
        )

    def construct_morphism(
        self,
        domain: RingsCategory.ObjectType,
        codomain: RingsCategory.ObjectType,
        carrier_morphism: MorphismCategory.ObjectType,
    ) -> RingsCategory.MorphismType:
        return self.MorphismType(
            self.morphism_category(1),
            domain,
            codomain,
            RingMorphismData(carrier_morphism),
        )

    def __call__(
        self,
        carrier: CategoryOfCategories.ElementType,
        addition: MorphismCategory.ObjectType,
        zero: MorphismCategory.ObjectType | CategoryOfCategories.ElementType,
        multiplication: MorphismCategory.ObjectType,
        one: MorphismCategory.ObjectType | CategoryOfCategories.ElementType,
        inversion: MorphismCategory.ObjectType,
    ) -> RingsCategory.ObjectType:
        key = tuple((id(value), value) for value in (carrier, addition, zero, multiplication, one, inversion))
        if key not in self._rings:
            self._rings[key] = self.ObjectType(
                category=self,
                data=RingObjectData(carrier, addition, zero, multiplication, one, inversion),
            )
        return self._rings[key]

    def __repr__(self) -> str:
        return f"Rings({self._ambient!r})"


_RING_CATEGORIES: MonoDict = MonoDict()


def Rings(ambient: Category) -> RingsCategory:
    """Construct or retrieve ``Rings(ambient)``, one category per ambient value."""
    if ambient not in _RING_CATEGORIES:
        _RING_CATEGORIES[ambient] = RingsCategory(ambient)
    return _RING_CATEGORIES[ambient]
