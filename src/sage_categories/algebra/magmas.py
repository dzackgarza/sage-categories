r"""``Magmas(V)``: internal magma objects in a monoidal category (``specs/magmas-monoids-semirings.md``).

An object of ``Magmas(V)`` is an object ``X`` of ``C`` equipped with a multiplication
morphism ``mu_X: X \otimes X -> X``.  A morphism is an arrow ``f: X -> Y`` in ``C``
such that ``f \circ mu_X = mu_Y \circ (f \otimes f)``.

The structure functor to ``C`` is the first product projection:
``Magmas(V).product_projection(0)`` (specs/magmas-monoids-semirings.md).

The notation subcategories ``Magmas(V).Additive()`` and ``Magmas(V).Multiplicative()``
expose ``+`` and ``*`` on generalized elements and points.
"""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sage.rings.integer import Integer
from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, predicate
from sage_categories.cat.properties import PropertySubcategory

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.cat.functors import Functor

# A private retention key: identity pairs ``(id(v), v)``, so cache lookups compare
# owned values by identity and never ask their proposition-valued equality
# (POL-SAGE-013).
type Key = tuple[Hashable, ...]


# Operation preservation predicate for magma morphisms: f \circ mu_X = mu_Y \circ (f \otimes f)
preserves_magma_operation: Predicate = predicate("preserves_magma_operation")


@dataclass(frozen=True, eq=False, slots=True)
class MagmaObjectData:
    """The carrier and multiplication morphism of a magma object.

    Every descendant construction datum threaded through the compiled magma
    implementation exposes these two names (``kernel/compiler.py`` initializes each
    reached implementation class with the one root datum).
    """

    carrier: CategoryOfCategories.ElementType
    multiplication: MorphismCategory.ObjectType

    @property
    def action_morphism(self) -> MorphismCategory.ObjectType:
        """The action the compiled module occurrence reads when the ambient is a module category: the carrier module's action."""
        return self.carrier.action_morphism()


class MagmaObjectDeclaration:
    """An object in ``Magmas(V)``."""

    def __init__(self, data: MagmaObjectData) -> None:
        self._carrier = data.carrier
        self._multiplication = data.multiplication
        super().__init__()

    def carrier(self) -> CategoryOfCategories.ElementType:
        return self._carrier

    def multiplication(self) -> MorphismCategory.ObjectType:
        r"""``mu_X: X \otimes X -> X``."""
        return self._multiplication

    def __repr__(self) -> str:
        return f"Magma({self._carrier!r})"


@dataclass(frozen=True, eq=False, slots=True)
class MagmaMorphismData:
    """A morphism in ``Magmas(V)``."""

    carrier_morphism: MorphismCategory.ObjectType


class MagmaMorphismDeclaration:
    """A morphism in ``Magmas(V)``."""

    def __init__(self, data: MagmaMorphismData) -> None:
        self._carrier_morphism = data.carrier_morphism
        super().__init__()

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
        return self._carrier_morphism

    def __repr__(self) -> str:
        return f"MagmaMorphism({self.domain()!r} -> {self.codomain()!r})"


class MagmasCategory(Category[[], []]):
    """``Magmas(V)``: internal magmas in a tensor or monoidal category ``V``."""

    ObjectType = MagmaObjectDeclaration
    MorphismType = MagmaMorphismDeclaration

    class ElementType:
        """A generalized element of a magma object."""

    def __init__(self, ambient: Category) -> None:
        self._ambient = ambient
        self._magmas: dict[Key, MagmasCategory.ObjectType] = {}
        super().__init__()
        self._additive = PropertySubcategory(self, "Additive", ())
        self._multiplicative = PropertySubcategory(self, "Multiplicative", ())
        self._commutative = PropertySubcategory(self, "Commutative", ())
        self._additive.Commutative = lambda: self._commutative
        self._multiplicative.Commutative = lambda: self._commutative

    def ambient(self) -> Category:
        return self._ambient

    def Additive(self) -> PropertySubcategory:
        return self._additive

    def Multiplicative(self) -> PropertySubcategory:
        return self._multiplicative

    def Commutative(self) -> PropertySubcategory:
        return self._commutative

    def product_projection(self, index: int | Integer) -> Functor:
        """The projection functor to the ambient category ``V`` (specs/magmas-monoids-semirings.md)."""
        assert index == 0, f"Magmas only has product projection 0, got {index}"
        ambient = self._ambient

        def on_object(M: MagmasCategory.ObjectType) -> CategoryOfCategories.ElementType:
            return M.carrier()

        def on_morphism(f: MagmasCategory.MorphismType) -> MorphismCategory.ObjectType:
            return f.carrier_morphism()

        return Fun(self, ambient)(on_object, on_morphism)

    def structure_functors(self) -> tuple[Functor, ...]:
        """Structure functor tuple: (self.product_projection(0),)."""
        return (self.product_projection(0),)

    def construct_morphism(
        self,
        domain: MagmasCategory.ObjectType,
        codomain: MagmasCategory.ObjectType,
        carrier_morphism: MorphismCategory.ObjectType,
    ) -> MagmasCategory.MorphismType:
        return self.MorphismType(
            self.morphism_category(1),
            domain,
            codomain,
            MagmaMorphismData(carrier_morphism),
        )

    def __call__(
        self,
        carrier: CategoryOfCategories.ElementType,
        multiplication: MorphismCategory.ObjectType,
    ) -> MagmasCategory.ObjectType:
        key = ((id(carrier), carrier), (id(multiplication), multiplication))
        if key not in self._magmas:
            self._magmas[key] = self.ObjectType(category=self, data=MagmaObjectData(carrier, multiplication))
        return self._magmas[key]

    def __repr__(self) -> str:
        return f"Magmas({self._ambient!r})"


_MAGMA_CATEGORIES: MonoDict = MonoDict()


def Magmas(ambient: Category) -> MagmasCategory:
    """Construct or retrieve ``Magmas(ambient)``, one category per ambient value."""
    if ambient not in _MAGMA_CATEGORIES:
        _MAGMA_CATEGORIES[ambient] = MagmasCategory(ambient)
    return _MAGMA_CATEGORIES[ambient]
