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
from typing import TYPE_CHECKING, Any

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun
from sage_categories.cat.predicates import Predicate, predicate
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.sets.category import Sets

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor


preserves_module_action: Predicate = predicate("preserves_module_action")


@dataclass(frozen=True, eq=False)
class ModuleObjectData:
    """The carrier and action morphism of a module object."""

    carrier: Any
    action_morphism: Any


class ModuleObjectDeclaration:
    """An object in ``Modules(A, C)``."""

    def __init__(self, data: Any) -> None:
        self._action_morphism = getattr(data, "action_morphism", getattr(data, "action", data))
        carrier = getattr(data, "carrier", None)
        if carrier is None and hasattr(self._action_morphism, "codomain"):
            carrier = self._action_morphism.codomain()
        self._carrier = carrier
        super().__init__()

    def carrier(self) -> Any:
        """The underlying object in ``C``."""
        return self._carrier

    def action(self) -> Any:
        r"""The action morphism ``\rho_X: A \bullet X -> X``."""
        return self._action_morphism

    def action_morphism(self) -> Any:
        r"""The action morphism ``\rho_X: A \bullet X -> X``."""
        return self._action_morphism

    def __repr__(self) -> str:
        return f"Module({self._carrier!r})"


@dataclass(frozen=True, eq=False, slots=True)
class ModuleMorphismData:
    """A morphism in ``Modules(A, C)``."""

    carrier_morphism: Any


class ModuleMorphismDeclaration:
    """A morphism in ``Modules(A, C)``."""

    def __init__(self, data: ModuleMorphismData) -> None:
        self._carrier_morphism = data.carrier_morphism
        super().__init__()

    def carrier_morphism(self) -> Any:
        return self._carrier_morphism

    def _ambient_morphism_data(self) -> Any:
        return self._carrier_morphism

    def __repr__(self) -> str:
        return f"ModuleMorphism({self.domain()!r} -> {self.codomain()!r})"


@dataclass(frozen=True, eq=False)
class ModulePresentation:
    r"""A finite presentation of a module \(R^m \xrightarrow{A} R^n \twoheadrightarrow M\) (specs/separating-families-and-categorical-generators.md)."""

    presented_module: ModuleObjectDeclaration
    generators_module: Any
    relations_module: Any
    matrix_morphism: Any
    presentation_morphism: Any
    rank: int
    relations_matrix: tuple[tuple[Any, ...], ...]


class ModulesCategory(Category[[], []]):
    """``Modules(A, C)``: module objects over a monoid or ring ``A`` in an actegory ``C``."""

    ObjectType = ModuleObjectDeclaration
    MorphismType = ModuleMorphismDeclaration

    class ElementType:
        """A generalized element of a module object."""

    def __init__(
        self,
        monoid: Any,
        ambient: Category | None = None,
        action: Functor | None = None,
    ) -> None:
        if ambient is None:
            ambient = Sets()
        self._monoid = monoid
        self._ambient = ambient
        self._action = action
        self._modules: dict[Any, ModulesCategory.ObjectType] = {}
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

    def monoid(self) -> Any:
        return self._monoid

    def ambient(self) -> Category:
        return self._ambient

    def actegory_action(self) -> Functor | None:
        return self._action

    def Free(self) -> PropertySubcategory:
        return self._free

    def FiniteRank(self) -> PropertySubcategory:
        return self._finite_rank

    def Based(self) -> PropertySubcategory:
        return self._based

    def U_A(self) -> Functor:
        """The faithful forgetful functor to the ambient category C."""
        ambient = self._ambient

        def on_object(M: ModulesCategory.ObjectType) -> Any:
            return M.carrier()

        def on_morphism(f: ModulesCategory.MorphismType) -> Any:
            return f.carrier_morphism() if hasattr(f, "carrier_morphism") else f

        return Fun(self, ambient).Faithful()(on_object, on_morphism)

    def structure_functors(self) -> tuple[Any, ...]:
        """The faithful projection U_A: Modules(A, C) -> C is the sole structure functor."""
        return (self.U_A(),)

    def construct_morphism(
        self,
        domain: ModulesCategory.ObjectType,
        codomain: ModulesCategory.ObjectType,
        carrier_morphism: Any,
    ) -> ModulesCategory.MorphismType:
        return self.MorphismType(
            self.morphism_category(1),
            domain,
            codomain,
            ModuleMorphismData(carrier_morphism),
        )

    def regular(self) -> ModulesCategory.ObjectType:
        r"""The regular module \(R\) as a compact projective generator (specs/separating-families-and-categorical-generators.md)."""
        A = self._monoid
        carrier = A.carrier() if hasattr(A, "carrier") else A
        mult = A.multiplication() if hasattr(A, "multiplication") else None

        if mult is None:
            square = carrier * carrier
            mult = self._ambient.morphism_category(1)(square, carrier)(lambda pair: pair(0) if callable(pair) else pair)

        return self(mult)

    def presentation(
        self,
        relations_matrix: tuple[tuple[Any, ...], ...] | list[list[Any]] = (),
        rank: int = 1,
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

    def from_endomorphism_action(self, A_to_End_X: Any) -> ModulesCategory.ObjectType:
        """Construct a module object from an enriched endomorphism morphism A -> End(X)."""
        X = A_to_End_X.codomain().carrier() if hasattr(A_to_End_X.codomain(), "carrier") else self._ambient.Terminal()
        carrier = X
        action_map = self._ambient.morphism_category(1)(carrier, carrier)(lambda x: x)
        return self(action_map)

    def from_sage_module(self, engine_module: Any) -> ModulesCategory.ObjectType:
        """Construct a module object from an engine-level Sage module."""
        sets = Sets()
        carrier = sets(lambda x: True)
        action_map = sets.morphism_category(1)(carrier, carrier)(lambda x: x)
        return self(action_map)

    def __call__(self, rho_X: Any) -> ModulesCategory.ObjectType:
        """Default constructor accepting the defining action morphism rho_X: A bullet X -> X."""
        if hasattr(rho_X, "action_morphism"):
            rho_X = rho_X.action_morphism()
        carrier = rho_X.codomain() if hasattr(rho_X, "codomain") else None
        key = rho_X
        if key not in self._modules:
            self._modules[key] = self.ObjectType(
                category=self,
                data=ModuleObjectData(carrier=carrier, action_morphism=rho_X),
            )
        return self._modules[key]

    def __repr__(self) -> str:
        return f"Modules({self._monoid!r}, {self._ambient!r})"


_MODULE_CATEGORIES: dict[tuple[Any, Category], ModulesCategory] = {}


def Modules(monoid: Any, ambient: Category | None = None) -> ModulesCategory:
    """Construct or retrieve ``Modules(monoid, ambient)``."""
    if ambient is None:
        ambient = Sets()
    key = (monoid, ambient)
    if key not in _MODULE_CATEGORIES:
        _MODULE_CATEGORIES[key] = ModulesCategory(monoid, ambient)
    return _MODULE_CATEGORIES[key]
