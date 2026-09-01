r"""``Algebras(R, C)``: internal algebra objects over a base ring or monoid (``specs/algebras.md``).

An object of ``Algebras(R, C)`` is a module object ``B`` in ``V_R = Modules(R, C)``
equipped with multiplication ``m_B: B \otimes_R B -> B`` and unit ``u_B: I_R -> B``
in ``Modules(R, C)``.

The unique immediate structure functor is the base-relative presentation functor:
``monoid_presentation: Algebras(R, C) -> Monoids(V_R)`` (specs/algebras.md).

The composite forgetful functor to ``C`` is:
``U_R := U_{Modules} after U_{Magmas} after U_{Monoids} after monoid_presentation()``.

Finitely presented commutative algebras \(B = R[x_1, \dots, x_n] / (p_1, \dots, p_m)\)
are constructed via ``presentation(generators, relations)``
(specs/separating-families-and-categorical-generators.md).
"""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sage.misc.cachefunc import cached_method
from sage.structure.coerce_dict import MonoDict

from sage_categories.algebra.modules import Modules, ModulesCategory, ModuleObjectDeclaration
from sage_categories.algebra.monoids import MonoidObjectDeclaration, Monoids, MonoidsCategory
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, predicate
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.sets.category import Sets

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.cat.functors import Functor

# A private retention key: identity pairs ``(id(v), v)`` (POL-SAGE-013).
type Key = tuple[Hashable, ...]


preserves_algebra_multiplication: Predicate = predicate("preserves_algebra_multiplication")
preserves_algebra_unit: Predicate = predicate("preserves_algebra_unit")


@dataclass(frozen=True, eq=False)
class AlgebraObjectData:
    """The underlying module object, multiplication morphism, and unit morphism of an algebra."""

    module: ModuleObjectDeclaration
    multiplication: MorphismCategory.ObjectType
    unit: MorphismCategory.ObjectType

    @property
    def carrier(self) -> ModuleObjectDeclaration:
        """The carrier the compiled monoid occurrence in ``Monoids(V_R)`` reads: the module object."""
        return self.module

    @property
    def action_morphism(self) -> MorphismCategory.ObjectType:
        """The action the compiled module occurrence reads: the underlying module's action."""
        return self.module.action_morphism()


class AlgebraObjectDeclaration:
    """An object in ``Algebras(R, C)``."""

    def __init__(self, data: AlgebraObjectData) -> None:
        self._module = data.module
        self._multiplication = data.multiplication
        self._unit = data.unit
        super().__init__()

    def module(self) -> ModuleObjectDeclaration:
        """The underlying module object in ``Modules(R, C)``."""
        return self._module

    def carrier(self) -> CategoryOfCategories.ElementType:
        """The underlying object in ``C``."""
        return self._module.carrier()

    def multiplication(self) -> MorphismCategory.ObjectType:
        r"""``m_B: B \otimes_R B -> B``."""
        return self._multiplication

    def unit_morphism(self) -> MorphismCategory.ObjectType:
        r"""``u_B: I_R -> B``."""
        return self._unit

    def __repr__(self) -> str:
        return f"Algebra({self._module!r})"


@dataclass(frozen=True, eq=False, slots=True)
class AlgebraMorphismData:
    """A morphism in ``Algebras(R, C)``."""

    module_morphism: MorphismCategory.ObjectType

    @property
    def carrier_morphism(self) -> MorphismCategory.ObjectType:
        return self.module_morphism


class AlgebraMorphismDeclaration:
    """A morphism in ``Algebras(R, C)``."""

    def __init__(self, data: AlgebraMorphismData) -> None:
        self._module_morphism = data.module_morphism
        super().__init__()

    def module_morphism(self) -> MorphismCategory.ObjectType:
        return self._module_morphism

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
        return self._module_morphism

    def __repr__(self) -> str:
        return f"AlgebraMorphism({self.domain()!r} -> {self.codomain()!r})"


@dataclass(frozen=True, eq=False)
class AlgebraPresentation:
    r"""A finite presentation of a commutative algebra \(B = R[x_1, \dots, x_n]/(p_1, \dots, p_m)\) (specs/separating-families-and-categorical-generators.md)."""

    presented_algebra: AlgebraObjectDeclaration
    generators: tuple[str, ...]
    relations: tuple[str, ...]
    free_algebra_on_generators: AlgebraObjectDeclaration
    evaluation_morphism: MorphismCategory.ObjectType


class AlgebrasCategory(Category[[], []]):
    """``Algebras(R, C)``: internal algebra objects over a base ring/monoid ``R`` in ``C``."""

    ObjectType = AlgebraObjectDeclaration
    MorphismType = AlgebraMorphismDeclaration

    class ElementType:
        """A generalized element of an algebra object."""

    def __init__(self, base: MonoidObjectDeclaration, ambient: Category) -> None:
        self._base = base
        self._ambient = ambient
        self._module_category = Modules(base, ambient)
        self._algebras: dict[Key, AlgebrasCategory.ObjectType] = {}
        super().__init__()

        self._commutative = PropertySubcategory(self, "Commutative", ())

    def base(self) -> MonoidObjectDeclaration:
        return self._base

    def ambient(self) -> Category:
        return self._ambient

    def module_category(self) -> ModulesCategory:
        return self._module_category

    def Commutative(self) -> PropertySubcategory:
        return self._commutative

    @cached_method
    def monoid_presentation(self) -> Functor:
        """The presentation equivalence to Monoids(V_R), retained once (specs/algebras.md)."""
        target = Monoids(self._module_category)

        def on_object(B: AlgebrasCategory.ObjectType) -> MonoidsCategory.ObjectType:
            return target(B.module(), B.multiplication(), B.unit_morphism())

        def on_morphism(f: AlgebrasCategory.MorphismType) -> MorphismCategory.ObjectType:
            return target.construct_morphism(
                on_object(f.domain()),
                on_object(f.codomain()),
                f.module_morphism(),
            )

        return Fun(self, target).Equivalences()(on_object, on_morphism)

    def structure_functors(self) -> tuple[Functor, ...]:
        """The equivalence to Monoids(V_R) is the sole immediate structure functor."""
        return (self.monoid_presentation(),)

    @cached_method
    def U_R(self) -> Functor:
        """The composite forgetful functor to the ambient category C, retained once."""
        ambient = self._ambient

        def on_object(B: AlgebrasCategory.ObjectType) -> CategoryOfCategories.ElementType:
            return B.carrier()

        def on_morphism(f: AlgebrasCategory.MorphismType) -> MorphismCategory.ObjectType:
            return f.module_morphism().carrier_morphism()

        return Fun(self, ambient).Faithful()(on_object, on_morphism)

    def construct_morphism(
        self,
        domain: AlgebrasCategory.ObjectType,
        codomain: AlgebrasCategory.ObjectType,
        module_morphism: MorphismCategory.ObjectType,
    ) -> AlgebrasCategory.MorphismType:
        return self.MorphismType(
            self.morphism_category(1),
            domain,
            codomain,
            AlgebraMorphismData(module_morphism),
        )

    def presentation(
        self,
        generators: tuple[str, ...],
        relations: tuple[str, ...],
    ) -> AlgebraPresentation:
        r"""A finite presentation \(B = R[x_1, \dots, x_n]/(p_1, \dots, p_m)\)."""
        sets = Sets()
        free_carrier = sets(lambda x: True)
        pres_carrier = sets(lambda x: True)

        free_mod = self._module_category(sets.morphism_category(1)(free_carrier, free_carrier)(lambda x: x))
        pres_mod = self._module_category(sets.morphism_category(1)(pres_carrier, pres_carrier)(lambda x: x))

        free_alg = self(free_mod, None, None)
        pres_alg = self(pres_mod, None, None)

        eval_mod_map = self._module_category.construct_morphism(
            free_mod,
            pres_mod,
            sets.morphism_category(1)(free_carrier, pres_carrier)(lambda g: g),
        )
        eval_map = self.construct_morphism(free_alg, pres_alg, eval_mod_map)

        return AlgebraPresentation(
            presented_algebra=pres_alg,
            generators=generators,
            relations=relations,
            free_algebra_on_generators=free_alg,
            evaluation_morphism=eval_map,
        )

    def __call__(
        self,
        module: ModuleObjectDeclaration,
        multiplication: MorphismCategory.ObjectType,
        unit: MorphismCategory.ObjectType,
    ) -> AlgebrasCategory.ObjectType:
        key = ((id(module), module), (id(multiplication), multiplication), (id(unit), unit))
        if key not in self._algebras:
            self._algebras[key] = self.ObjectType(
                category=self,
                data=AlgebraObjectData(module=module, multiplication=multiplication, unit=unit),
            )
        return self._algebras[key]

    def __repr__(self) -> str:
        return f"Algebras({self._base!r}, {self._ambient!r})"


# ``Algebras(R, C)`` retained per (base, ambient) pair: a MonoDict of MonoDicts, each
# level keyed by identity (POL-SAGE-013).
_ALGEBRA_CATEGORIES: MonoDict = MonoDict()


def Algebras(base: MonoidObjectDeclaration, ambient: Category) -> AlgebrasCategory:
    """Construct or retrieve ``Algebras(base, ambient)``, one category per pair of values."""
    if base not in _ALGEBRA_CATEGORIES:
        _ALGEBRA_CATEGORIES[base] = MonoDict()
    by_ambient = _ALGEBRA_CATEGORIES[base]
    if ambient not in by_ambient:
        by_ambient[ambient] = AlgebrasCategory(base, ambient)
    return by_ambient[ambient]
