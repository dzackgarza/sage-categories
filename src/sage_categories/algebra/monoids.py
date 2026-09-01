r"""``Monoids(V)``: internal monoid objects in a monoidal category (``specs/magmas-monoids-semirings.md``).

An object of ``Monoids(V)`` is an object ``X`` in ``C`` equipped with:
- a multiplication morphism ``mu_X: X \otimes X -> X``
- a unit morphism ``eta_X: I -> X``
satisfying the associativity and unit diagrams in ``C``.

The notation subcategories are:
- ``Monoids(V).Additive()``, which exposes ``zero()`` (when ``I`` is terminal) and ``+``
- ``Monoids(V).Multiplicative()``, which exposes ``one()`` and ``*``
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sage_categories.algebra.magmas import Magmas
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.predicates import Predicate, predicate
from sage_categories.cat.properties import PropertySubcategory

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor


preserves_monoid_unit: Predicate = predicate("preserves_monoid_unit")


@dataclass(frozen=True, eq=False, slots=True)
class MonoidObjectData:
    """The carrier, multiplication morphism, and unit morphism of a monoid object."""

    carrier: Any
    multiplication: Any
    unit: Any


class MonoidObjectDeclaration:
    """An object in ``Monoids(V)``."""

    def __init__(self, data: MonoidObjectData) -> None:
        self._carrier = data.carrier
        self._multiplication = data.multiplication
        self._unit = data.unit
        super().__init__()

    def carrier(self) -> Any:
        return self._carrier

    def multiplication(self) -> Any:
        """``mu_X: X \otimes X -> X``."""
        return self._multiplication

    def unit_morphism(self) -> Any:
        """``eta_X: I -> X``."""
        return self._unit

    def zero(self) -> Any:
        """The additive unit point."""
        return self._unit

    def one(self) -> Any:
        """The multiplicative unit point."""
        return self._unit

    def __repr__(self) -> str:
        return f"Monoid({self._carrier!r})"


class MonoidsCategory(Category[[], []]):
    """``Monoids(V)``: internal monoid objects in a monoidal category ``V``."""

    ObjectType = MonoidObjectDeclaration

    def __init__(self, ambient: Category) -> None:
        self._ambient = ambient
        self._monoids: dict[Any, MonoidsCategory.ObjectType] = {}
        super().__init__()
        self._additive = PropertySubcategory(self, "Additive", ())
        self._multiplicative = PropertySubcategory(self, "Multiplicative", ())
        self._commutative_additive = PropertySubcategory(self._additive, "Commutative", ())
        self._commutative_multiplicative = PropertySubcategory(self._multiplicative, "Commutative", ())

    def ambient(self) -> Category:
        return self._ambient

    def Additive(self) -> PropertySubcategory:
        return self._additive

    def Multiplicative(self) -> PropertySubcategory:
        return self._multiplicative

    def structure_functors(self) -> tuple[Any, ...]:
        """Structure functor to Magmas(ambient)."""
        magmas = Magmas(self._ambient)
        return (Fun(self, magmas).Monomorphisms().Isofibrations()(),)

    def __call__(self, carrier: Any, multiplication: Any, unit: Any) -> MonoidsCategory.ObjectType:
        key = (carrier, multiplication, unit)
        if key not in self._monoids:
            self._monoids[key] = self.ObjectType(category=self, data=MonoidObjectData(carrier, multiplication, unit))
        return self._monoids[key]

    def __repr__(self) -> str:
        return f"Monoids({self._ambient!r})"


_MONOID_CATEGORIES: dict[Category, MonoidsCategory] = {}


def Monoids(ambient: Category) -> MonoidsCategory:
    """Construct or retrieve ``Monoids(ambient)``."""
    if ambient not in _MONOID_CATEGORIES:
        _MONOID_CATEGORIES[ambient] = MonoidsCategory(ambient)
    return _MONOID_CATEGORIES[ambient]
