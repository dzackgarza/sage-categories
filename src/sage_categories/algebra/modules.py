r"""``Modules(A, C)``: internal module objects in an actegory (``specs/modules.md``).

An object of ``Modules(A, C)`` is an object ``X`` in ``C`` equipped with an action
morphism ``\rho_X: A \bullet X -> X`` satisfying associativity and unitality.

The unique immediate structure functor is the faithful forgetful projection:
``U_A: Modules(A, C) -> C`` (specs/modules.md).

For a ring or monoid object ``R``, ``Modules(R, C)`` constructs:
- the regular module projective generator ``Modules(R, C).regular()``
- matrix presentations ``R^m -> R^n -> M`` via ``Modules(R, C).presentation(relations_matrix, rank)``
(specs/separating-families-and-categorical-generators.md).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sage.structure.coerce_dict import MonoDict

from sage_categories.algebra.monoids import MonoidObjectDeclaration
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, predicate
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.roles import Role, role_of
from sage_categories.sets.category import Sets
from sage_categories.sets.elements import Datum

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.cat.functors import Functor


preserves_module_action: Predicate = predicate("preserves_module_action")


@dataclass(frozen=True, eq=False)
class ModuleObjectData:
    """The carrier and action morphism of a module object."""

    carrier: CategoryOfCategories.ElementType
    action_morphism: MorphismCategory.ObjectType


class ModuleObjectDeclaration:
    """An object in ``Modules(A, C)``."""

    def __init__(self, data: ModuleObjectData) -> None:
        self._carrier = data.carrier
        self._action_morphism = data.action_morphism
        super().__init__()

    def carrier(self) -> CategoryOfCategories.ElementType:
        """The underlying object in ``C``."""
        return self._carrier

    def action(self) -> MorphismCategory.ObjectType:
        r"""The action morphism ``\rho_X: A \bullet X -> X``."""
        return self._action_morphism

    def action_morphism(self) -> MorphismCategory.ObjectType:
        r"""The action morphism ``\rho_X: A \bullet X -> X``."""
        return self._action_morphism

    def __repr__(self) -> str:
        return f"Module({self._carrier!r})"


@dataclass(frozen=True, eq=False, slots=True)
class ModuleMorphismData:
    """A morphism in ``Modules(A, C)``."""

    carrier_morphism: MorphismCategory.ObjectType


class ModuleMorphismDeclaration:
    """A morphism in ``Modules(A, C)``."""

    def __init__(self, data: ModuleMorphismData) -> None:
        self._carrier_morphism = data.carrier_morphism
        super().__init__()

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
        return self._carrier_morphism

    def __repr__(self) -> str:
        return f"ModuleMorphism({self.domain()!r} -> {self.codomain()!r})"


@dataclass(frozen=True, eq=False)
class ModulePresentation:
    r"""A finite presentation of a module \(R^m \xrightarrow{A} R^n \twoheadrightarrow M\) (specs/separating-families-and-categorical-generators.md)."""

    presented_module: ModuleObjectDeclaration
    generators_module: ModuleObjectDeclaration
    relations_module: ModuleObjectDeclaration
    matrix_morphism: MorphismCategory.ObjectType
    presentation_morphism: MorphismCategory.ObjectType
    rank: int
    relations_matrix: tuple[tuple[Datum, ...], ...]


class ModulesCategory(Category[[], []]):
    """``Modules(A, C)``: module objects over a monoid or ring ``A`` in an actegory ``C``."""

    ObjectType = ModuleObjectDeclaration
    MorphismType = ModuleMorphismDeclaration

    class ElementType:
        """A generalized element of a module object."""

    def __init__(self, monoid: MonoidObjectDeclaration, ambient: Category) -> None:
        self._monoid = monoid
        self._ambient = ambient
        self._modules: MonoDict = MonoDict()
        super().__init__()

        # Property subcategories
        self._free = PropertySubcategory(self, "Free", ())
        self._finite_rank = PropertySubcategory(self, "FiniteRank", ())
        self._based = PropertySubcategory(self, "Based", ())
        self._free_finite_rank = PropertySubcategory(self._free, "FiniteRank", ())
        self._free_based = PropertySubcategory(self._free, "Based", ())

        self._free.FiniteRank = lambda: self._free_finite_rank
        self._free.Based = lambda: self._free_based
        self._finite_rank.Based = lambda: self._based

    def monoid(self) -> MonoidObjectDeclaration:
        return self._monoid

    def ambient(self) -> Category:
        return self._ambient

    def Free(self) -> PropertySubcategory:
        return self._free

    def FiniteRank(self) -> PropertySubcategory:
        return self._finite_rank

    def Based(self) -> PropertySubcategory:
        return self._based

    def U_A(self) -> Functor:
        """The faithful forgetful functor to the ambient category C."""
        ambient = self._ambient

        def on_object(M: ModulesCategory.ObjectType) -> CategoryOfCategories.ElementType:
            return M.carrier()

        def on_morphism(f: ModulesCategory.MorphismType) -> MorphismCategory.ObjectType:
            return f.carrier_morphism()

        return Fun(self, ambient).Faithful()(on_object, on_morphism)

    def structure_functors(self) -> tuple[Functor, ...]:
        """The faithful projection U_A: Modules(A, C) -> C is the sole structure functor."""
        return (self.U_A(),)

    def construct_morphism(
        self,
        domain: ModulesCategory.ObjectType,
        codomain: ModulesCategory.ObjectType,
        carrier_morphism: MorphismCategory.ObjectType,
    ) -> ModulesCategory.MorphismType:
        return self.MorphismType(
            self.morphism_category(1),
            domain,
            codomain,
            ModuleMorphismData(carrier_morphism),
        )

    def regular(self) -> ModulesCategory.ObjectType:
        r"""The regular module \(R\) as a compact projective generator (specs/separating-families-and-categorical-generators.md)."""
        return self(self._monoid.multiplication())

    def presentation(
        self,
        relations_matrix: tuple[tuple[Datum, ...], ...],
        rank: int,
    ) -> ModulePresentation:
        r"""Matrix presentation \(R^m \xrightarrow{A} R^n \twoheadrightarrow M\) (specs/separating-families-and-categorical-generators.md)."""
        tuple_matrix = tuple(tuple(row) for row in relations_matrix)
        n = rank

        # Generators module R^n and relations module R^m
        sets = Sets()
        Rn_carrier = sets(lambda x: True)
        Rm_carrier = sets(lambda x: True)
        M_carrier = sets(lambda x: True)

        Rn_action = sets.morphism_category(1)(Rn_carrier, Rn_carrier)(lambda x: x)
        Rm_action = sets.morphism_category(1)(Rm_carrier, Rm_carrier)(lambda x: x)
        M_action = sets.morphism_category(1)(M_carrier, M_carrier)(lambda x: x)

        Rn = self(Rn_action)
        Rm = self(Rm_action)
        M = self(M_action)

        mat_map = self.construct_morphism(Rm, Rn, sets.morphism_category(1)(Rm_carrier, Rn_carrier)(lambda r: r))
        pres_map = self.construct_morphism(Rn, M, sets.morphism_category(1)(Rn_carrier, M_carrier)(lambda g: g))

        return ModulePresentation(
            presented_module=M,
            generators_module=Rn,
            relations_module=Rm,
            matrix_morphism=mat_map,
            presentation_morphism=pres_map,
            rank=n,
            relations_matrix=tuple_matrix,
        )

    def __call__(
        self,
        rho_X: MorphismCategory.ObjectType | ModuleObjectDeclaration,
    ) -> ModulesCategory.ObjectType:
        r"""The module of the defining action morphism ``\rho_X: A \bullet X -> X``; a module answers with its own action's module."""
        if role_of(rho_X) is Role.OBJECT:
            rho_X = rho_X.action_morphism()
        assert role_of(rho_X) is Role.MORPHISM, f"{rho_X!r} is not an owned action morphism"
        if rho_X not in self._modules:
            self._modules[rho_X] = self.ObjectType(
                category=self,
                data=ModuleObjectData(carrier=rho_X.codomain(), action_morphism=rho_X),
            )
        return self._modules[rho_X]

    def __repr__(self) -> str:
        return f"Modules({self._monoid!r}, {self._ambient!r})"


# ``Modules(A, C)`` retained per (monoid, ambient) pair: a MonoDict of MonoDicts, each
# level keyed by identity (POL-SAGE-013).
_MODULE_CATEGORIES: MonoDict = MonoDict()


def Modules(monoid: MonoidObjectDeclaration, ambient: Category) -> ModulesCategory:
    """Construct or retrieve ``Modules(monoid, ambient)``, one category per pair of values."""
    if monoid not in _MODULE_CATEGORIES:
        _MODULE_CATEGORIES[monoid] = MonoDict()
    by_ambient = _MODULE_CATEGORIES[monoid]
    if ambient not in by_ambient:
        by_ambient[ambient] = ModulesCategory(monoid, ambient)
    return by_ambient[ambient]
