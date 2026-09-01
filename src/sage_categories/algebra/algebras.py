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

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sage_categories.algebra.modules import Modules, ModulesCategory
from sage_categories.algebra.monoids import Monoids
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun
from sage_categories.cat.predicates import Predicate, predicate
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.sets.category import Sets

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor


preserves_algebra_multiplication: Predicate = predicate("preserves_algebra_multiplication")
preserves_algebra_unit: Predicate = predicate("preserves_algebra_unit")


@dataclass(frozen=True, eq=False)
class AlgebraObjectData:
    """The underlying module object, multiplication morphism, and unit morphism of an algebra."""

    module: Any
    multiplication: Any
    unit: Any

    @property
    def carrier(self) -> Any:
        return self.module


class AlgebraObjectDeclaration:
    """An object in ``Algebras(R, C)``."""

    def __init__(self, data: Any) -> None:
        self._module = getattr(data, "module", getattr(data, "carrier", data))
        self._multiplication = getattr(data, "multiplication", None)
        self._unit = getattr(data, "unit", getattr(data, "unit_morphism", None))
        super().__init__()

    def module(self) -> Any:
        """The underlying module object in ``Modules(R, C)``."""
        return self._module

    def carrier(self) -> Any:
        """The underlying object in ``C``."""
        if hasattr(self._module, "carrier"):
            return self._module.carrier()
        return self._module

    def multiplication(self) -> Any:
        r"""``m_B: B \otimes_R B -> B``."""
        return self._multiplication

    def unit_morphism(self) -> Any:
        r"""``u_B: I_R -> B``."""
        return self._unit

    def __repr__(self) -> str:
        return f"Algebra({self._module!r})"


@dataclass(frozen=True, eq=False, slots=True)
class AlgebraMorphismData:
    """A morphism in ``Algebras(R, C)``."""

    module_morphism: Any

    @property
    def carrier_morphism(self) -> Any:
        return self.module_morphism


class AlgebraMorphismDeclaration:
    """A morphism in ``Algebras(R, C)``."""

    def __init__(self, data: Any) -> None:
        self._module_morphism = getattr(data, "module_morphism", getattr(data, "carrier_morphism", data))
        super().__init__()

    def module_morphism(self) -> Any:
        return self._module_morphism

    def carrier_morphism(self) -> Any:
        return self._module_morphism

    def __repr__(self) -> str:
        return f"AlgebraMorphism({self.domain()!r} -> {self.codomain()!r})"


@dataclass(frozen=True, eq=False)
class AlgebraPresentation:
    r"""A finite presentation of a commutative algebra \(B = R[x_1, \dots, x_n]/(p_1, \dots, p_m)\) (specs/separating-families-and-categorical-generators.md)."""

    presented_algebra: AlgebraObjectDeclaration
    generators: tuple[str, ...]
    relations: tuple[Any, ...]
    free_algebra_on_generators: Any
    evaluation_morphism: Any


class AlgebrasCategory(Category[[], []]):
    """``Algebras(R, C)``: internal algebra objects over a base ring/monoid ``R`` in ``C``."""

    ObjectType = AlgebraObjectDeclaration
    MorphismType = AlgebraMorphismDeclaration

    class ElementType:
        """A generalized element of an algebra object."""

    def __init__(
        self,
        base: Any,
        ambient: Category | None = None,
        module_category: ModulesCategory | None = None,
    ) -> None:
        if ambient is None:
            ambient = Sets()
        self._base = base
        self._ambient = ambient
        if module_category is None:
            module_category = Modules(base, ambient)
        self._module_category = module_category
        self._algebras: dict[Any, AlgebrasCategory.ObjectType] = {}
        super().__init__()

        self._commutative = PropertySubcategory(self, "Commutative", ())

    def base(self) -> Any:
        return self._base

    def ambient(self) -> Category:
        return self._ambient

    def module_category(self) -> ModulesCategory:
        return self._module_category

    def Commutative(self) -> PropertySubcategory:
        return self._commutative

    def monoid_presentation(self) -> Functor:
        """The presentation equivalence to Monoids(V_R) (specs/algebras.md)."""
        target = Monoids(self._module_category)

        def on_object(B: AlgebrasCategory.ObjectType) -> Any:
            return target(B.module(), B.multiplication(), B.unit_morphism())

        def on_morphism(f: AlgebrasCategory.MorphismType) -> Any:
            return target.construct_morphism(
                on_object(f.domain()),
                on_object(f.codomain()),
                f.module_morphism() if hasattr(f, "module_morphism") else f,
            )

        return Fun(self, target).Equivalences()(on_object, on_morphism)

    def structure_functors(self) -> tuple[Any, ...]:
        """The equivalence to Monoids(V_R) is the sole immediate structure functor."""
        return (self.monoid_presentation(),)

    def U_R(self) -> Functor:
        """The composite forgetful functor to the ambient category C."""
        ambient = self._ambient

        def on_object(B: AlgebrasCategory.ObjectType) -> Any:
            return B.carrier()

        def on_morphism(f: AlgebrasCategory.MorphismType) -> Any:
            m = f.module_morphism() if hasattr(f, "module_morphism") else f
            return m.carrier_morphism() if hasattr(m, "carrier_morphism") else m

        return Fun(self, ambient).Faithful()(on_object, on_morphism)

    def construct_morphism(
        self,
        domain: AlgebrasCategory.ObjectType,
        codomain: AlgebrasCategory.ObjectType,
        module_morphism: Any,
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
        relations: tuple[Any, ...] = (),
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
        module: Any,
        multiplication: Any = None,
        unit: Any = None,
    ) -> AlgebrasCategory.ObjectType:
        key = (module, multiplication, unit)
        if key not in self._algebras:
            self._algebras[key] = self.ObjectType(
                category=self,
                data=AlgebraObjectData(module=module, multiplication=multiplication, unit=unit),
            )
        return self._algebras[key]

    def __repr__(self) -> str:
        return f"Algebras({self._base!r}, {self._ambient!r})"


_ALGEBRA_CATEGORIES: dict[tuple[Any, Category], AlgebrasCategory] = {}


def Algebras(base: Any, ambient: Category | None = None) -> AlgebrasCategory:
    """Construct or retrieve ``Algebras(base, ambient)``."""
    if ambient is None:
        ambient = Sets()
    key = (base, ambient)
    if key not in _ALGEBRA_CATEGORIES:
        _ALGEBRA_CATEGORIES[key] = AlgebrasCategory(base, ambient)
    return _ALGEBRA_CATEGORIES[key]
