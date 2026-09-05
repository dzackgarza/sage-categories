"""Module objects over a monoid object acting through a selected actegory.

``Modules(A, C)`` for ``A`` a monoid object of a monoidal category ``M`` and ``C`` a selected
left ``M``-actegory: the algebras ``ρ: A • X -> X`` of the endofunctor ``A • -`` that satisfy
the unit and action laws (``specs/modules.md``; nLab, module object, "Definition /
Generalisation").  The laws are equifiers over the endofunctor-algebra inserter, as the
monoid laws are over pointed magmas.
"""

from __future__ import annotations

__all__ = ["ModuleCategory", "Modules"]

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.calculus import pair_maps
from sage_categories.cat.monoidal import ActionsCategory, tensor_morphism
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import EndofunctorAlgebras, Equifier, EquifierCategory, InserterCategory, MonoidCategory, Monoids
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method


def _scalar_endofunctor(actegory: ActionsCategory.ObjectType, scalar: CategoryOfCategories.ElementType) -> Functor:
    """``m • -: C -> C`` for an object ``m`` of the acting monoidal category."""
    base = actegory.underlying_category()
    constant = Fun(base, actegory.monoidal_structure().underlying_category()).constant(scalar)
    return actegory.action() * pair_maps(Cat(), constant, Fun(base, base).one())


def _underlying_object(scalars: MonoidCategory.ObjectType) -> CategoryOfCategories.ElementType:
    """The object of ``M`` carrying a monoid object."""
    return scalars.carrier().carrier()


def _underlying_morphism(monoids: MonoidCategory, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    """The morphism of ``M`` carrying a monoid morphism."""
    magmas = monoids.to_magmas().codomain()
    return magmas.forgetful().on_morphism(monoids.to_magmas().on_morphism(arrow))


class ModuleCategory(EquifierCategory):
    """``Modules(A, C)``: module objects over ``A`` in the actegory ``C``.

    An object is ``(X, ρ_X: A • X -> X)`` with the unit law ``ρ ∘ (η • X) = λ_X`` and the
    action law ``ρ ∘ (μ • X) = ρ ∘ (A • ρ) ∘ a_{A,A,X}``; a morphism is ``f: X -> Y`` in
    ``C`` with ``f ∘ ρ_X = ρ_Y ∘ (A • f)``.  ``forgetful()`` is ``U_A``, the inserter's
    projection to ``C``, which carries inheritance.
    """

    class ObjectType:
        def action(self) -> MorphismCategory.ObjectType:
            """``ρ_X: A • X -> X``, the module action."""
            return self.structure()

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(
        self,
        first: NaturalTransformation,
        second: NaturalTransformation,
        scalars: MonoidCategory.ObjectType,
        actegory: ActionsCategory.ObjectType,
        algebras: InserterCategory,
    ) -> None:
        self._scalars, self._actegory, self._algebras = scalars, actegory, algebras
        super().__init__(first, second)

    def scalars(self) -> MonoidCategory.ObjectType:
        """``A``, the monoid object acting."""
        return self._scalars

    def actegory(self) -> ActionsCategory.ObjectType:
        """The selected left ``M``-action on ``C`` with its coherence isomorphisms."""
        return self._actegory

    def underlying_category(self) -> Category:
        return self._actegory.underlying_category()

    @cached_method
    def forgetful(self) -> Functor:
        """``U_A: Modules(A, C) -> C``, ``(X, ρ_X) ↦ X`` and ``f ↦ f``."""
        return self._algebras.forgetful() * Fun.full_subcategory_monomorphism(self, self._algebras)

    def __call__(self, action_morphism: MorphismCategory.ObjectType) -> ModuleCategory.ObjectType:
        """The module with action ``ρ_X: A • X -> X``; its codomain is ``X``."""
        return super().__call__(self._algebras.algebra(action_morphism.codomain(), action_morphism))

    def homomorphism(
        self,
        source: ModuleCategory.ObjectType,
        target: ModuleCategory.ObjectType,
        arrow: MorphismCategory.ObjectType,
    ) -> ModuleCategory.MorphismType:
        """The module morphism over ``f: X -> Y`` in ``C``; the algebra square ``f ∘ ρ_X = ρ_Y ∘ (A • f)`` must commute."""
        return self._algebras.homomorphism(source, target, arrow)

    def transport(self, module: ModuleCategory.ObjectType, isomorphism: MorphismCategory.ObjectType) -> ModuleCategory.ObjectType:
        """The module on ``Y`` along an isomorphism ``φ: X -> Y`` of ``C``: ``ρ_Y = φ ∘ ρ_X ∘ (A • φ⁻¹)``."""
        base = self.underlying_category()
        assert isomorphism.domain() is self.forgetful().on_object(module)
        assert isomorphism in base.morphism_category(1).Isomorphisms(), f"{isomorphism!r} is not an isomorphism of {base!r}"
        identity = base.morphism_category(1)(_underlying_object(self._scalars), _underlying_object(self._scalars)).one()
        return self(isomorphism * module.action() * tensor_morphism(self._actegory.action(), identity, isomorphism.inverse()))

    @cached_method(key=identity_key)
    def restriction(self, scalar_morphism: MorphismCategory.ObjectType) -> Functor:
        """Restriction of scalars along a monoid morphism ``f: B -> A``: ``Modules(A, C) -> Modules(B, C)``, ``(X, ρ) ↦ (X, ρ ∘ (f • X))``."""
        monoids = Monoids(self._actegory.monoidal_structure())
        assert scalar_morphism.codomain() is self._scalars, f"{scalar_morphism!r} does not end at {self._scalars!r}"
        target = Modules(scalar_morphism.domain(), self._actegory)
        underlying = _underlying_morphism(monoids, scalar_morphism)
        base = self.underlying_category()

        def on_object(module: ModuleCategory.ObjectType) -> ModuleCategory.ObjectType:
            carrier = self.forgetful().on_object(module)
            return target(module.action() * tensor_morphism(self._actegory.action(), underlying, base.morphism_category(1)(carrier, carrier).one()))

        def on_morphism(arrow: ModuleCategory.MorphismType) -> ModuleCategory.MorphismType:
            return target.homomorphism(on_object(arrow.domain()), on_object(arrow.codomain()), self.forgetful().on_morphism(arrow))

        return Fun(self, target)(on_object, on_morphism)


@cached_function(key=identity_key)
def Modules(scalars: MonoidCategory.ObjectType, actegory: ActionsCategory.ObjectType) -> ModuleCategory:
    """``Modules(A, C)``: module objects over the monoid object ``A`` in the selected actegory ``C``."""
    monoidal = actegory.monoidal_structure()
    monoids = Monoids(monoidal)
    assert scalars in monoids, f"{scalars!r} is not a monoid object of {monoidal.underlying_category()!r}"
    base, action = actegory.underlying_category(), actegory.action()
    carrier = _underlying_object(scalars)
    operation, unit = scalars.operation(), scalars.unit_morphism()
    algebras = EndofunctorAlgebras(_scalar_endofunctor(actegory, carrier))
    forget = algebras.forgetful()
    identity_scalar = monoidal.underlying_category().morphism_category(1)(carrier, carrier).one()

    def unit_law(value: CategoryOfCategories.ElementType, law: bool) -> MorphismCategory.ObjectType:
        """``ρ ∘ (η • X)`` and ``λ_X`` on ``I • X``."""
        x, rho = value.carrier(), value.structure()
        if law:
            return rho * tensor_morphism(action, unit, base.morphism_category(1)(x, x).one())
        return actegory.unitor().component(x)

    def action_law(value: CategoryOfCategories.ElementType, law: bool) -> MorphismCategory.ObjectType:
        """``ρ ∘ (μ • X)`` and ``ρ ∘ (A • ρ) ∘ a_{A,A,X}`` on ``(A ⊗ A) • X``."""
        x, rho = value.carrier(), value.structure()
        if law:
            return rho * tensor_morphism(action, operation, base.morphism_category(1)(x, x).one())
        triples = actegory.associator().domain().domain()
        return rho * tensor_morphism(action, identity_scalar, rho) * actegory.associator().component(triples((carrier, carrier, x)))

    transformations = Fun(algebras, base).morphism_category(1)
    unit_source = _scalar_endofunctor(actegory, monoidal.unit()) * forget
    square_source = _scalar_endofunctor(actegory, monoidal.tensor().on_object(monoidal.tensor().domain()((carrier, carrier)))) * forget
    equations = (
        (transformations(unit_source, forget)(lambda value: unit_law(value, True)), transformations(unit_source, forget)(lambda value: unit_law(value, False))),
        (transformations(square_source, forget)(lambda value: action_law(value, True)), transformations(square_source, forget)(lambda value: action_law(value, False))),
    )
    unital = Equifier(*equations[0])
    inclusion = Fun.full_subcategory_monomorphism(unital, algebras)
    first, second = equations[1]
    return ModuleCategory(first.whisker_right(inclusion), second.whisker_right(inclusion), scalars, actegory, algebras)
