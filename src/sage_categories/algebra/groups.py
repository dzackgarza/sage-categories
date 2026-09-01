"""``Groups(V)``: internal group objects in a cartesian monoidal category (``specs/magmas-monoids-semirings.md``).

An object of ``Groups(V)`` is a monoid object ``X`` in ``Monoids(V)`` equipped with
an inversion morphism ``iota_X: X -> X`` satisfying the left and right inverse diagrams.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sage_categories.algebra.monoids import Monoids, MonoidsCategory
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun
from sage_categories.cat.properties import PropertySubcategory


@dataclass(frozen=True, eq=False, slots=True)
class GroupObjectData:
    """The carrier, multiplication, unit, and inversion morphism of a group object."""

    carrier: Any
    multiplication: Any
    unit: Any
    inversion: Any


class GroupObjectDeclaration:
    """An object in ``Groups(V)``."""

    def __init__(self, data: GroupObjectData) -> None:
        self._carrier = data.carrier
        self._multiplication = data.multiplication
        self._unit = data.unit
        self._inversion = data.inversion
        super().__init__()

    def carrier(self) -> Any:
        return self._carrier

    def multiplication(self) -> Any:
        return self._multiplication

    def unit_morphism(self) -> Any:
        return self._unit

    def inversion(self) -> Any:
        """``iota_X: X -> X``."""
        return self._inversion

    def zero(self) -> Any:
        return self._unit

    def one(self) -> Any:
        return self._unit

    def __repr__(self) -> str:
        return f"Group({self._carrier!r})"


class GroupsCategory(Category[[], []]):
    """``Groups(V)``: internal group objects in a cartesian monoidal category ``V``."""

    ObjectType = GroupObjectDeclaration

    class ElementType:
        """A generalized element of a group object."""

    class MorphismType:
        """A morphism of groups."""

    def __init__(self, ambient: Category) -> None:
        self._ambient = ambient
        self._groups: dict[Any, GroupsCategory.ObjectType] = {}
        super().__init__()
        self._additive = PropertySubcategory(self, "Additive", ())
        self._multiplicative = PropertySubcategory(self, "Multiplicative", ())
        self._commutative_additive = PropertySubcategory(self._additive, "Commutative", ())

    def ambient(self) -> Category:
        return self._ambient

    def Additive(self) -> PropertySubcategory:
        return self._additive

    def Multiplicative(self) -> PropertySubcategory:
        return self._multiplicative

    def structure_functors(self) -> tuple[Any, ...]:
        """Structure functor to Monoids(ambient)."""
        monoids = Monoids(self._ambient)
        return (Fun(self, monoids).Monomorphisms().Isofibrations().Full()(),)

    def __call__(self, carrier: Any, multiplication: Any, unit: Any, inversion: Any) -> GroupsCategory.ObjectType:
        key = (carrier, multiplication, unit, inversion)
        if key not in self._groups:
            self._groups[key] = self.ObjectType(category=self, data=GroupObjectData(carrier, multiplication, unit, inversion))
        return self._groups[key]

    def __repr__(self) -> str:
        return f"Groups({self._ambient!r})"


_GROUP_CATEGORIES: dict[Category, GroupsCategory] = {}


def Groups(ambient: Category) -> GroupsCategory:
    """Construct or retrieve ``Groups(ambient)``."""
    if ambient not in _GROUP_CATEGORIES:
        _GROUP_CATEGORIES[ambient] = GroupsCategory(ambient)
    return _GROUP_CATEGORIES[ambient]
