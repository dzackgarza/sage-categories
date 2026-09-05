"""Inserters and equifiers, and algebraic structures expressed through them.

Inserters are pullbacks of comma categories along the diagonal on objects
and morphisms. Equifiers impose component equations as full subcategories.
Reference: Bird, Kelly, Power and Street, Flexible limits for 2-categories.
"""

from __future__ import annotations

__all__ = [
    "InserterCategory",
    "Inserter",
    "EquifierCategory",
    "Equifier",
    "EndofunctorAlgebras",
    "Magmas",
    "PointedMagmas",
    "Monoids",
    "MonoidCategory",
    "EilenbergMoore",
]

from sage_categories.cat.cat_constructions import LimitSubcategory, limit_of_categories
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.comma import comma_objects
from sage_categories.cat.cones import cone
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.calculus import pair_maps
from sage_categories.cat.monoidal import Cartesian, MonoidalStructuresCategory, tensor_morphism, tensor_parentheses, tensor_units
from sage_categories.cat.predicates import ask
from sage_categories.cat.properties import FullSubcategory
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method


class InserterCategory(LimitSubcategory):
    class ObjectType:
        def carrier(self) -> CategoryOfCategories.ElementType:
            return self.family_component(0)

        def structure(self) -> MorphismCategory.ObjectType:
            return self.family_component(1).arrow()

    class ElementType:
        pass

    class MorphismType:
        def underlying_morphism(self) -> MorphismCategory.ObjectType:
            return self.family_component(0)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (*super().structure_functors(), self.forgetful())

    @cached_method(key=identity_key)
    def algebra(
        self,
        carrier: CategoryOfCategories.ElementType,
        structure: MorphismCategory.ObjectType,
    ) -> InserterCategory.ObjectType:
        comma = self.factor(1)
        pair = self.factor(2)((carrier, carrier))
        return self((carrier, comma.from_arrow(carrier, carrier, structure), pair))

    def homomorphism(
        self,
        source: CategoryOfCategories.ElementType,
        target: CategoryOfCategories.ElementType,
        arrow: MorphismCategory.ObjectType,
    ) -> InserterCategory.MorphismType:
        comma, pairs = self.factor(1), self.factor(2)
        return self.construct_morphism(
            source,
            target,
            (
                arrow,
                comma.morphism_from_pair(
                    source.family_component(1), target.family_component(1), arrow, arrow
                ),
                pairs.construct_morphism(
                    source.family_component(2), target.family_component(2), (arrow, arrow)
                ),
            ),
        )

    @cached_method
    def forgetful(self) -> Functor:
        return Fun(self, self.factor(0)).Faithful().Isofibrations()(
            lambda value: value.carrier(), lambda arrow: arrow.underlying_morphism()
        )

    @cached_method
    def defining_transformation(self) -> NaturalTransformation:
        first, second = self.factor(1).comma_functors()
        return Mor(Fun(self, first.codomain()))(
            first * self.forgetful(), second * self.forgetful()
        )(lambda value: value.structure())


@cached_function(key=identity_key)
def Inserter(first: Functor, second: Functor) -> InserterCategory:
    assert first.domain() is second.domain() and first.codomain() is second.codomain()
    source = first.domain()
    comma = comma_objects(first, second)
    pairs = Cat().Products()((source, source))
    factors = pairs.product_factors()
    diagonal = pairs.universal_morphism(
        cone(factors, source, lambda vertex: Fun(source, source).one())
    )
    diagram = cospan_diagram(Cat(), diagonal, comma.pair_projection())
    return limit_of_categories(diagram, Cat().Pullbacks(), InserterCategory)


class EquifierCategory(FullSubcategory):
    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(
        self, first: NaturalTransformation, second: NaturalTransformation
    ) -> None:
        assert (
            first.domain() is second.domain() and first.codomain() is second.codomain()
        )
        self._equations = (first, second)
        super().__init__(first.domain().domain())

    def __call__(
        self, value: CategoryOfCategories.ElementType
    ) -> CategoryOfCategories.ElementType:
        if isinstance(self.ambient(), EquifierCategory):
            self.ambient()(value)
        assert value in self.ambient()
        first, second = self._equations
        assert ask(first.component(value) == second.component(value)) is True
        refine(value, self)
        return value


@cached_function(key=identity_key)
def Equifier(
    first: NaturalTransformation, second: NaturalTransformation
) -> EquifierCategory:
    return EquifierCategory(first, second)


@cached_function(key=identity_key)
def EndofunctorAlgebras(endofunctor: Functor) -> InserterCategory:
    """Algebras of an endofunctor, without imposed unit or multiplication laws."""
    assert endofunctor.domain() is endofunctor.codomain()
    return Inserter(endofunctor, Fun(endofunctor.domain(), endofunctor.domain()).one())


@cached_function(key=identity_key)
def Magmas(structure: Functor | MonoidalStructuresCategory.ObjectType) -> InserterCategory:
    """Multiplications ``X ⊗ X -> X`` for a specified tensor bifunctor."""
    if not isinstance(structure, Functor):
        return Magmas(structure.tensor())
    tensor = structure
    source = tensor.codomain()
    pairs = tensor.domain()
    assert (
        pairs.product_projection(0).codomain() is source
        and pairs.product_projection(1).codomain() is source
    )
    diagonal = pair_maps(Cat(), Fun(source, source).one(), Fun(source, source).one())
    return EndofunctorAlgebras(tensor * diagonal)


@cached_function(key=identity_key)
def PointedMagmas(
    tensor: Functor, unit: CategoryOfCategories.ElementType
) -> InserterCategory:
    """A multiplication together with a map from the specified unit object."""
    magmas = Magmas(tensor)
    return Inserter(Fun(magmas, tensor.codomain()).constant(unit), magmas.forgetful())


class MonoidCategory(EquifierCategory):
    """Monoid objects with multiplication and unit in their supplied ambient."""

    class ObjectType:
        def multiplication(self) -> MorphismCategory.ObjectType:
            return self.carrier().structure()

        def unit_morphism(self) -> MorphismCategory.ObjectType:
            return self.structure()

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, first: NaturalTransformation, second: NaturalTransformation, monoidal: MonoidalStructuresCategory.ObjectType) -> None:
        self._monoidal = monoidal
        super().__init__(first, second)

    def monoidal_structure(self) -> MonoidalStructuresCategory.ObjectType:
        return self._monoidal

    def __call__(self, multiplication: MorphismCategory.ObjectType, unit: MorphismCategory.ObjectType) -> MonoidCategory.ObjectType:
        monoidal = self.monoidal_structure()
        magma = Magmas(monoidal).algebra(multiplication.codomain(), multiplication)
        pointed = PointedMagmas(monoidal.tensor(), monoidal.unit()).algebra(magma, unit)
        return super().__call__(pointed)

    @cached_method
    def to_magmas(self) -> Functor:
        monoidal = self.monoidal_structure()
        pointed = PointedMagmas(monoidal.tensor(), monoidal.unit())
        return pointed.forgetful() * Fun.full_subcategory_monomorphism(self, pointed)


@cached_function(key=identity_key)
def Monoids(structure: Category | MonoidalStructuresCategory.ObjectType) -> MonoidCategory:
    """Monoid objects for the supplied tensor, unit, associator, and unitors."""
    if isinstance(structure, Category):
        return Monoids(Cartesian(structure))
    base, tensor = structure.underlying_category(), structure.tensor()
    pointed = PointedMagmas(tensor, structure.unit())
    forget = Magmas(tensor).forgetful() * pointed.forgetful()

    def unital(
        value: CategoryOfCategories.ElementType, left: bool
    ) -> MorphismCategory.ObjectType:
        carrier = value.carrier().carrier()
        multiplication, unit = value.carrier().structure(), value.structure()
        identity = Mor(base)(carrier, carrier).one()
        return multiplication * tensor_morphism(
            tensor, unit if left else identity, identity if left else unit
        )

    def associative(
        value: CategoryOfCategories.ElementType, left: bool
    ) -> MorphismCategory.ObjectType:
        carrier, multiplication = value.carrier().carrier(), value.carrier().structure()
        identity = Mor(base)(carrier, carrier).one()
        if left:
            return multiplication * tensor_morphism(tensor, multiplication, identity)
        associator = structure.associator().component(
            structure.associator().domain().domain()((carrier, carrier, carrier)))
        return multiplication * tensor_morphism(tensor, identity, multiplication) * associator

    transformations = Mor(Fun(pointed, base))
    left_unit, right_unit = tensor_units(tensor, structure.unit())
    triples = structure.associator().domain().domain()
    diagonal = triples.universal_morphism(cone(
        triples.product_factors(), base, lambda vertex: Fun(base, base).one()))
    cube = tensor_parentheses(tensor)[0] * diagonal * forget
    equations = (
        (transformations(left_unit * forget, forget)(lambda value: unital(value, True)), structure.left_unitor().whisker_right(forget)),
        (transformations(right_unit * forget, forget)(lambda value: unital(value, False)), structure.right_unitor().whisker_right(forget)),
        (
            transformations(cube, forget)(lambda value: associative(value, True)),
            transformations(cube, forget)(lambda value: associative(value, False)),
        ),
    )
    result = pointed
    for first, second in equations[:-1]:
        inclusion = (
            Fun.full_subcategory_monomorphism(result, pointed)
            if result is not pointed
            else Fun(pointed, pointed).one()
        )
        result = Equifier(
            first.whisker_right(inclusion), second.whisker_right(inclusion)
        )
    inclusion = Fun.full_subcategory_monomorphism(result, pointed)
    first, second = equations[-1]
    return MonoidCategory(first.whisker_right(inclusion), second.whisker_right(inclusion), structure)


@cached_function(key=identity_key)
def EilenbergMoore(
    endofunctor: Functor,
    unit: NaturalTransformation,
    multiplication: NaturalTransformation,
) -> EquifierCategory:
    """Algebras of the supplied monad, with both algebra laws imposed by equifiers.

    The supplied unit and multiplication must satisfy the monad laws.
    Reference: Mathlib CategoryTheory.Monad.Algebra.
    """
    base = endofunctor.domain()
    assert endofunctor.codomain() is base
    assert unit.domain() is Fun(base, base).one() and unit.codomain() is endofunctor
    assert (
        multiplication.domain() is endofunctor * endofunctor
        and multiplication.codomain() is endofunctor
    )
    algebras = EndofunctorAlgebras(endofunctor)
    forget = algebras.forgetful()
    action = algebras.defining_transformation()
    unital = Equifier(
        action * unit.whisker_right(forget),
        Mor(Fun(algebras, base))(forget, forget).one(),
    )
    inclusion = Fun.full_subcategory_monomorphism(unital, algebras)
    left = (action * multiplication.whisker_right(forget)).whisker_right(inclusion)
    right = (action * action.whisker_left(endofunctor)).whisker_right(inclusion)
    return Equifier(left, right)
