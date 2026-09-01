r"""``Magmas(V)``: internal magma objects in a monoidal category (``specs/magmas-monoids-semirings.md``).

An object of ``Magmas(V)`` is an object ``X`` of ``C`` equipped with a multiplication
morphism ``mu_X: X \otimes X -> X``.  A morphism is an arrow ``f: X -> Y`` in ``C``
such that ``f \circ mu_X = mu_Y \circ (f \otimes f)``.

The notation subcategories ``Magmas(V).Additive()`` and ``Magmas(V).Multiplicative()``
expose ``+`` and ``*`` on generalized elements and points.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sage_categories.cat.category import Category
from sage_categories.cat.predicates import Predicate, predicate
from sage_categories.cat.properties import PropertySubcategory

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor


# Operation preservation predicate for magma morphisms: f \circ mu_X = mu_Y \circ (f \otimes f)
preserves_magma_operation: Predicate = predicate("preserves_magma_operation")


@dataclass(frozen=True, eq=False, slots=True)
class MagmaObjectData:
    """The carrier and multiplication morphism of a magma object."""

    carrier: Any
    multiplication: Any


class MagmaObjectDeclaration:
    """An object in ``Magmas(V)``."""

    def __init__(self, data: MagmaObjectData) -> None:
        self._carrier = data.carrier
        self._multiplication = data.multiplication
        super().__init__()

    def carrier(self) -> Any:
        return self._carrier

    def multiplication(self) -> Any:
        """``mu_X: X \otimes X -> X``."""
        return self._multiplication

    def __repr__(self) -> str:
        return f"Magma({self._carrier!r})"


class MagmasCategory(Category[[], []]):
    """``Magmas(V)``: internal magmas in a tensor or monoidal category ``V``."""

    ObjectType = MagmaObjectDeclaration

    class ElementType:
        """A generalized element of a magma object."""

    class MorphismType:
        """A morphism of magmas."""

    def __init__(self, ambient: Category) -> None:
        self._ambient = ambient
        self._magmas: dict[Any, MagmasCategory.ObjectType] = {}
        super().__init__()
        self._additive = PropertySubcategory(self, "Additive", ())
        self._multiplicative = PropertySubcategory(self, "Multiplicative", ())
        self._commutative = PropertySubcategory(self, "Commutative", ())

    def ambient(self) -> Category:
        return self._ambient

    def Additive(self) -> PropertySubcategory:
        return self._additive

    def Multiplicative(self) -> PropertySubcategory:
        return self._multiplicative

    def Commutative(self) -> PropertySubcategory:
        return self._commutative

    def __call__(self, carrier: Any, multiplication: Any) -> MagmasCategory.ObjectType:
        key = (carrier, multiplication)
        if key not in self._magmas:
            self._magmas[key] = self.ObjectType(category=self, data=MagmaObjectData(carrier, multiplication))
        return self._magmas[key]

    def __repr__(self) -> str:
        return f"Magmas({self._ambient!r})"


_MAGMA_CATEGORIES: dict[Category, MagmasCategory] = {}


def Magmas(ambient: Category) -> MagmasCategory:
    """Construct or retrieve ``Magmas(ambient)``."""
    if ambient not in _MAGMA_CATEGORIES:
        _MAGMA_CATEGORIES[ambient] = MagmasCategory(ambient)
    return _MAGMA_CATEGORIES[ambient]
