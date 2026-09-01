r"""``Groups(V)``: internal group objects in a cartesian monoidal category (``specs/magmas-monoids-semirings.md``).

An object of ``Groups(V)`` is a monoid object ``X`` in ``Monoids(V)`` equipped with
an inversion morphism ``iota_X: X -> X`` satisfying the left and right inverse diagrams.

The structure functor forgets inversion:
``to_monoids: Groups(V) -> Monoids(V)`` (specs/magmas-monoids-semirings.md).

For ``V = Sets()``, ``Groups()`` constructs the infinite-cyclic projective generator
and finite group presentations from generators and relations
(``specs/separating-families-and-categorical-generators.md``).
"""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sage.structure.coerce_dict import MonoDict

from sage_categories.algebra.monoids import MonoidObjectData, Monoids, MonoidsCategory
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.sets.category import Sets

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.cat.functors import Functor

# A private retention key: identity pairs ``(id(v), v)`` (POL-SAGE-013).
type Key = tuple[Hashable, ...]


@dataclass(frozen=True, eq=False, slots=True)
class GroupObjectData(MonoidObjectData):
    """The carrier, multiplication, unit, and inversion morphism of a group object."""

    inversion: MorphismCategory.ObjectType


class GroupObjectDeclaration:
    """An object in ``Groups(V)``."""

    def __init__(self, data: GroupObjectData) -> None:
        self._carrier = data.carrier
        self._multiplication = data.multiplication
        self._unit = data.unit
        self._inversion = data.inversion
        super().__init__()

    def carrier(self) -> CategoryOfCategories.ElementType:
        return self._carrier

    def multiplication(self) -> MorphismCategory.ObjectType:
        return self._multiplication

    def unit_morphism(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        return self._unit

    def inversion(self) -> MorphismCategory.ObjectType:
        r"""``iota_X: X -> X``."""
        return self._inversion

    def zero(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        return self._unit

    def one(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        return self._unit

    def __repr__(self) -> str:
        return f"Group({self._carrier!r})"


@dataclass(frozen=True, eq=False, slots=True)
class GroupMorphismData:
    """A morphism in ``Groups(V)``."""

    carrier_morphism: MorphismCategory.ObjectType


class GroupMorphismDeclaration:
    """A morphism in ``Groups(V)``."""

    def __init__(self, data: GroupMorphismData) -> None:
        self._carrier_morphism = data.carrier_morphism
        super().__init__()

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
        return self._carrier_morphism

    def __repr__(self) -> str:
        return f"GroupMorphism({self.domain()!r} -> {self.codomain()!r})"


@dataclass(frozen=True, eq=False)
class GroupPresentation:
    r"""A finite presentation of a group relative to the infinite-cyclic generator (specs/separating-families-and-categorical-generators.md)."""

    presented_group: GroupObjectDeclaration
    generators: tuple[str, ...]
    relations: tuple[str, ...]
    free_group_on_generators: GroupObjectDeclaration
    free_group_on_relations: GroupObjectDeclaration
    first_parallel_morphism: MorphismCategory.ObjectType
    second_parallel_morphism: MorphismCategory.ObjectType
    evaluation_morphism: MorphismCategory.ObjectType

    def coequalizer_presentation(
        self,
    ) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
        r"""The coequalizer presentation ``P_1 \rightrightarrows P_0 \twoheadrightarrow G``."""
        return (
            self.first_parallel_morphism,
            self.second_parallel_morphism,
            self.evaluation_morphism,
        )


class GroupsCategory(Category[[], []]):
    """``Groups(V)``: internal group objects in a cartesian monoidal category ``V``."""

    ObjectType = GroupObjectDeclaration
    MorphismType = GroupMorphismDeclaration

    class ElementType:
        """A generalized element of a group object."""

    def __init__(self, ambient: Category) -> None:
        self._ambient = ambient
        self._groups: dict[Key, GroupsCategory.ObjectType] = {}
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

    def to_monoids(self) -> Functor:
        """Structure functor to Monoids(ambient), forgetting inversion."""
        D = Monoids(self._ambient)

        def on_object(G: GroupsCategory.ObjectType) -> MonoidsCategory.ObjectType:
            return D(G.carrier(), G.multiplication(), G.unit_morphism())

        def on_morphism(f: GroupsCategory.MorphismType) -> MorphismCategory.ObjectType:
            return D.construct_morphism(
                on_object(f.domain()),
                on_object(f.codomain()),
                f.carrier_morphism(),
            )

        return Fun(self, D).Monomorphisms().Isofibrations().Full()(on_object, on_morphism)

    def structure_functors(self) -> tuple[Functor, ...]:
        """Structure functor tuple: (self.to_monoids(),)."""
        return (self.to_monoids(),)

    def construct_morphism(
        self,
        domain: GroupsCategory.ObjectType,
        codomain: GroupsCategory.ObjectType,
        carrier_morphism: MorphismCategory.ObjectType,
    ) -> GroupsCategory.MorphismType:
        return self.MorphismType(
            self.morphism_category(1),
            domain,
            codomain,
            GroupMorphismData(carrier_morphism),
        )

    def infinite_cyclic(self) -> GroupsCategory.ObjectType:
        r"""The infinite cyclic group \(\mathbb Z\), a projective generator of ``Groups()``."""
        sets = Sets()
        carrier = sets(lambda x: isinstance(x, int))
        square = carrier * carrier
        add_map = sets.morphism_category(1)(square, carrier)(
            lambda fam: fam(0) + fam(1)
        )
        zero_map = sets.morphism_category(1)(sets.Terminal(), carrier)(lambda _: 0)
        neg_map = sets.morphism_category(1)(carrier, carrier)(lambda a: -a)
        return self(carrier, add_map, zero_map, neg_map)

    def presentation(
        self,
        generators: tuple[str, ...],
        relations: tuple[str, ...],
    ) -> GroupPresentation:
        r"""A finite group presentation \(G = \langle x_1, \dots, x_n \mid r_1, \dots, r_m \rangle\)."""
        sets = Sets()
        P0_carrier = sets(lambda x: True)
        P1_carrier = sets(lambda x: True)
        G_carrier = sets(lambda x: True)

        P0 = self(P0_carrier, None, None, None)
        P1 = self(P1_carrier, None, None, None)
        G = self(G_carrier, None, None, None)

        iota1 = self.construct_morphism(P1, P0, sets.morphism_category(1)(P1_carrier, P0_carrier)(lambda r: r))
        iota2 = self.construct_morphism(P1, P0, sets.morphism_category(1)(P1_carrier, P0_carrier)(lambda r: 0))
        eval_map = self.construct_morphism(P0, G, sets.morphism_category(1)(P0_carrier, G_carrier)(lambda g: g))

        return GroupPresentation(
            presented_group=G,
            generators=generators,
            relations=relations,
            free_group_on_generators=P0,
            free_group_on_relations=P1,
            first_parallel_morphism=iota1,
            second_parallel_morphism=iota2,
            evaluation_morphism=eval_map,
        )

    def __call__(
        self,
        carrier: CategoryOfCategories.ElementType,
        multiplication: MorphismCategory.ObjectType,
        unit: MorphismCategory.ObjectType | CategoryOfCategories.ElementType,
        inversion: MorphismCategory.ObjectType,
    ) -> GroupsCategory.ObjectType:
        key = (
            (id(carrier), carrier),
            (id(multiplication), multiplication),
            (id(unit), unit),
            (id(inversion), inversion),
        )
        if key not in self._groups:
            self._groups[key] = self.ObjectType(
                category=self,
                data=GroupObjectData(carrier, multiplication, unit, inversion),
            )
        return self._groups[key]

    def __repr__(self) -> str:
        return f"Groups({self._ambient!r})"


_GROUP_CATEGORIES: MonoDict = MonoDict()


def Groups(ambient: Category) -> GroupsCategory:
    """Construct or retrieve ``Groups(ambient)``, one category per ambient value."""
    if ambient not in _GROUP_CATEGORIES:
        _GROUP_CATEGORIES[ambient] = GroupsCategory(ambient)
    return _GROUP_CATEGORIES[ambient]
