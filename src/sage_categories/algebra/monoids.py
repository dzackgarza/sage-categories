r"""``Monoids(V)``: internal monoid objects in a monoidal category (``specs/magmas-monoids-semirings.md``).

An object of ``Monoids(V)`` is an object ``X`` in ``C`` equipped with:
- a multiplication morphism ``mu_X: X \otimes X -> X``
- a unit morphism ``eta_X: I -> X``
satisfying the associativity and unit diagrams in ``C``.

The immediate structure functor forgets associativity and the unit:
``to_magmas: Monoids(V) -> Magmas(V)`` (specs/magmas-monoids-semirings.md).

The notation subcategories are:
- ``Monoids(V).Additive()``, which exposes ``zero()`` (when ``I`` is terminal) and ``+``
- ``Monoids(V).Multiplicative()``, which exposes ``one()`` and ``*``
"""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sage.misc.cachefunc import cached_method
from sage.structure.coerce_dict import MonoDict

from sage_categories.algebra.magmas import MagmaObjectData, Magmas, MagmasCategory
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, predicate
from sage_categories.cat.properties import PropertySubcategory

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.cat.functors import Functor

# A private retention key: identity pairs ``(id(v), v)`` (POL-SAGE-013).
type Key = tuple[Hashable, ...]


preserves_monoid_unit: Predicate = predicate("preserves_monoid_unit")


@dataclass(frozen=True, eq=False, slots=True)
class MonoidObjectData(MagmaObjectData):
    """The carrier, multiplication morphism, and unit morphism of a monoid object.

    Extending :class:`MagmaObjectData` states the exact contract the compiled magma
    implementation reads when the kernel threads this datum through it.
    """

    unit: MorphismCategory.ObjectType | CategoryOfCategories.ElementType


class MonoidObjectDeclaration:
    """An object in ``Monoids(V)``."""

    def __init__(self, data: MonoidObjectData) -> None:
        self._carrier = data.carrier
        self._multiplication = data.multiplication
        self._unit = data.unit
        super().__init__()

    def carrier(self) -> CategoryOfCategories.ElementType:
        return self._carrier

    def multiplication(self) -> MorphismCategory.ObjectType:
        r"""``mu_X: X \otimes X -> X``."""
        return self._multiplication

    def unit_morphism(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        r"""``eta_X: I -> X``, or the unit value it selects at a ``Cat()`` ambient."""
        return self._unit

    def zero(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        """The additive unit point."""
        return self._unit

    def one(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        """The multiplicative unit point."""
        return self._unit

    def __repr__(self) -> str:
        return f"Monoid({self._carrier!r})"


@dataclass(frozen=True, eq=False, slots=True)
class MonoidMorphismData:
    """A morphism in ``Monoids(V)``."""

    carrier_morphism: MorphismCategory.ObjectType


class MonoidMorphismDeclaration:
    """A morphism in ``Monoids(V)``."""

    def __init__(self, data: MonoidMorphismData) -> None:
        self._carrier_morphism = data.carrier_morphism
        super().__init__()

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
        return self._carrier_morphism

    def __repr__(self) -> str:
        return f"MonoidMorphism({self.domain()!r} -> {self.codomain()!r})"


class MonoidsCategory(Category[[], []]):
    """``Monoids(V)``: internal monoid objects in a monoidal category ``V``."""

    ObjectType = MonoidObjectDeclaration
    MorphismType = MonoidMorphismDeclaration

    class ElementType:
        """A generalized element of a monoid object."""

    def __init__(self, ambient: Category) -> None:
        self._ambient = ambient
        self._monoids: dict[Key, MonoidsCategory.ObjectType] = {}
        super().__init__()
        self._additive = PropertySubcategory(self, "Additive", ())
        self._multiplicative = PropertySubcategory(self, "Multiplicative", ())
        self._commutative_additive = PropertySubcategory(self._additive, "Commutative", ())
        self._commutative_multiplicative = PropertySubcategory(self._multiplicative, "Commutative", ())
        self._additive.Commutative = lambda: self._commutative_additive
        self._multiplicative.Commutative = lambda: self._commutative_multiplicative

    def ambient(self) -> Category:
        return self._ambient

    def Additive(self) -> PropertySubcategory:
        return self._additive

    def Multiplicative(self) -> PropertySubcategory:
        return self._multiplicative

    @cached_method
    def to_magmas(self) -> Functor:
        """Forgets unit and associativity: ``Monoids(V) -> Magmas(V)``, retained once."""
        D = Magmas(self._ambient)

        def on_object(M: MonoidsCategory.ObjectType) -> MagmasCategory.ObjectType:
            return D(M.carrier(), M.multiplication())

        def on_morphism(f: MonoidsCategory.MorphismType) -> MorphismCategory.ObjectType:
            return D.construct_morphism(
                on_object(f.domain()),
                on_object(f.codomain()),
                f.carrier_morphism(),
            )

        return Fun(self, D).Monomorphisms().Isofibrations()(on_object, on_morphism)

    def structure_functors(self) -> tuple[Functor, ...]:
        """Structure functor tuple: (self.to_magmas(),)."""
        return (self.to_magmas(),)

    def construct_morphism(
        self,
        domain: MonoidsCategory.ObjectType,
        codomain: MonoidsCategory.ObjectType,
        carrier_morphism: MorphismCategory.ObjectType,
    ) -> MonoidsCategory.MorphismType:
        return self.MorphismType(
            self.morphism_category(1),
            domain,
            codomain,
            MonoidMorphismData(carrier_morphism),
        )

    def __call__(
        self,
        carrier: CategoryOfCategories.ElementType,
        multiplication: MorphismCategory.ObjectType,
        unit: MorphismCategory.ObjectType | CategoryOfCategories.ElementType,
    ) -> MonoidsCategory.ObjectType:
        key = ((id(carrier), carrier), (id(multiplication), multiplication), (id(unit), unit))
        if key not in self._monoids:
            self._monoids[key] = self.ObjectType(category=self, data=MonoidObjectData(carrier, multiplication, unit))
        return self._monoids[key]

    def __repr__(self) -> str:
        return f"Monoids({self._ambient!r})"


_MONOID_CATEGORIES: MonoDict = MonoDict()


def Monoids(ambient: Category) -> MonoidsCategory:
    """Construct or retrieve ``Monoids(ambient)``, one category per ambient value."""
    if ambient not in _MONOID_CATEGORIES:
        _MONOID_CATEGORIES[ambient] = MonoidsCategory(ambient)
    return _MONOID_CATEGORIES[ambient]
