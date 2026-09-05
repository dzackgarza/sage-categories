"""Selected monoidal structures and actions, with their coherence morphisms.

The defining data and equations follow Mathlib's ``MonoidalCategoryStruct``
and ``MonoidalCategory``. Parameters form discrete categories of choices.
https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Monoidal/Category.html
"""

from __future__ import annotations

from typing import NamedTuple

from sage_categories.cat.calculus import binary_product_data, natural_isomorphism, pair_maps, product_functor, terminal_map
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.predicates import Proposition
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function

__all__ = ["MonoidalStructures", "MonoidalStructuresCategory", "Cartesian", "Composition", "Actions", "ActionsCategory", "SelfAction", "TrivialAction"]


def tensor_object(tensor: Functor, first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    return tensor.on_object(tensor.domain()((first, second)))


def tensor_morphism(tensor: Functor, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    pairs = tensor.domain()
    return tensor.on_morphism(Mor(pairs)(
        pairs((first.domain(), second.domain())),
        pairs((first.codomain(), second.codomain())),
    )((first, second)))


@cached_function(key=identity_key)
def tensor_parentheses(tensor: Functor) -> tuple[Functor, Functor]:
    base = tensor.codomain()
    triples = Cat().Products()((base, base, base))
    first, second, third = (triples.product_projection(index) for index in range(3))
    return (
        tensor * pair_maps(Cat(), tensor * pair_maps(Cat(), first, second), third),
        tensor * pair_maps(Cat(), first, tensor * pair_maps(Cat(), second, third)),
    )


@cached_function(key=identity_key)
def tensor_units(tensor: Functor, unit: CategoryOfCategories.ElementType) -> tuple[Functor, Functor]:
    base = tensor.codomain()
    identity = Fun(base, base).one()
    constant = Fun(base, base).constant(unit)
    return tensor * pair_maps(Cat(), constant, identity), tensor * pair_maps(Cat(), identity, constant)


class _MonoidalData(NamedTuple):
    tensor: Functor
    unit: CategoryOfCategories.ElementType
    associator: NaturalTransformation
    left_unitor: NaturalTransformation
    right_unitor: NaturalTransformation


class MonoidalStructuresCategory(Category[[], []]):
    """The discrete category of supplied coherent monoidal structures on C."""

    class ObjectType:
        def __init__(self, data: _MonoidalData) -> None:
            self._monoidal_data = data

        def underlying_category(self) -> Category:
            return self.tensor().codomain()

        def tensor(self) -> Functor:
            return self._monoidal_data.tensor

        def unit(self) -> CategoryOfCategories.ElementType:
            return self._monoidal_data.unit

        def associator(self) -> NaturalTransformation:
            return self._monoidal_data.associator

        def left_unitor(self) -> NaturalTransformation:
            return self._monoidal_data.left_unitor

        def right_unitor(self) -> NaturalTransformation:
            return self._monoidal_data.right_unitor

        def pentagon(self, w: CategoryOfCategories.ElementType, x: CategoryOfCategories.ElementType, y: CategoryOfCategories.ElementType, z: CategoryOfCategories.ElementType) -> Proposition:
            tensor, associator = self.tensor(), self.associator()
            triples = associator.domain().domain()
            a = lambda p, q, r: associator.component(triples((p, q, r)))
            wx, xy, yz = tensor_object(tensor, w, x), tensor_object(tensor, x, y), tensor_object(tensor, y, z)
            base = self.underlying_category()
            long = tensor_morphism(tensor, Mor(base)(w, w).one(), a(x, y, z)) * a(w, xy, z) * tensor_morphism(tensor, a(w, x, y), Mor(base)(z, z).one())
            short = a(w, x, yz) * a(wx, y, z)
            return long == short

        def triangle(self, x: CategoryOfCategories.ElementType, y: CategoryOfCategories.ElementType) -> Proposition:
            tensor, base = self.tensor(), self.underlying_category()
            associator = self.associator().component(self.associator().domain().domain()((x, self.unit(), y)))
            return tensor_morphism(tensor, Mor(base)(x, x).one(), self.left_unitor().component(y)) * associator == tensor_morphism(tensor, self.right_unitor().component(x), Mor(base)(y, y).one())

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, base: Category) -> None:
        self._base = base

    def __call__(self, tensor: Functor, unit: CategoryOfCategories.ElementType, associator: NaturalTransformation, left_unitor: NaturalTransformation, right_unitor: NaturalTransformation) -> MonoidalStructuresCategory.ObjectType:
        assert tensor.codomain() is self._base
        assert all(tensor.domain().product_projection(index).codomain() is self._base for index in (0, 1))
        assert unit in self._base
        left, right = tensor_parentheses(tensor)
        left_unit, right_unit = tensor_units(tensor, unit)
        identity = Fun(self._base, self._base).one()
        for comparison, source, target in ((associator, left, right), (left_unitor, left_unit, identity), (right_unitor, right_unit, identity)):
            assert comparison in Mor(Fun(source.domain(), self._base))(source, target).Isomorphisms()
        return self.ObjectType(_MonoidalData(tensor, unit, associator, left_unitor, right_unitor))

    def construct_morphism(self, source: MonoidalStructuresCategory.ObjectType, target: MonoidalStructuresCategory.ObjectType) -> MonoidalStructuresCategory.MorphismType:
        assert source is target, "a morphism in this discrete category is an identity"
        return self.MorphismType(domain=source, codomain=target)


@cached_function(key=identity_key)
def MonoidalStructures(base: Category) -> MonoidalStructuresCategory:
    return MonoidalStructuresCategory(base)


@cached_function(key=identity_key)
def Cartesian(base: Category) -> MonoidalStructuresCategory.ObjectType:
    tensor, unit = product_functor(base), base.Terminal()
    left, right = tensor_parentheses(tensor)

    def rebracket(triple: CategoryOfCategories.ElementType, forward: bool) -> MorphismCategory.ObjectType:
        x, y, z = (triple.component(index) for index in range(3))
        xy, yz = binary_product_data(base, x, y), binary_product_data(base, y, z)
        if forward:
            source = binary_product_data(base, xy.apex(), z)
            return pair_maps(base, xy.leg(0) * source.leg(0), pair_maps(base, xy.leg(1) * source.leg(0), source.leg(1)))
        source = binary_product_data(base, x, yz.apex())
        return pair_maps(base, pair_maps(base, source.leg(0), yz.leg(0) * source.leg(1)), yz.leg(1) * source.leg(1))

    associator = natural_isomorphism(left, right, lambda triple: rebracket(triple, True), lambda triple: rebracket(triple, False))
    left_unit, right_unit = tensor_units(tensor, unit)
    identity = Fun(base, base).one()
    left_unitor = natural_isomorphism(left_unit, identity,
        lambda x: binary_product_data(base, unit, x).leg(1),
        lambda x: pair_maps(base, terminal_map(base, x), Mor(base)(x, x).one()))
    right_unitor = natural_isomorphism(right_unit, identity,
        lambda x: binary_product_data(base, x, unit).leg(0),
        lambda x: pair_maps(base, Mor(base)(x, x).one(), terminal_map(base, x)))
    return MonoidalStructures(base)(tensor, unit, associator, left_unitor, right_unitor)


@cached_function(key=identity_key)
def Composition(base: Category) -> MonoidalStructuresCategory.ObjectType:
    endofunctors = Fun(base, base)
    pairs = Cat().Products()((endofunctors, endofunctors))
    tensor = Fun(pairs, endofunctors)(
        lambda pair: pair.component(0) * pair.component(1),
        lambda arrow: Cat().horizontal_composite(arrow.component(0), arrow.component(1)))
    unit = endofunctors.one()
    left, right = tensor_parentheses(tensor)
    left_unit, right_unit = tensor_units(tensor, unit)
    identity = Fun(endofunctors, endofunctors).one()

    def comparison(first: Functor, second: Functor) -> NaturalTransformation:
        return natural_isomorphism(first, second,
            lambda x: Mor(endofunctors)(first.on_object(x), second.on_object(x)).one(),
            lambda x: Mor(endofunctors)(second.on_object(x), first.on_object(x)).one())

    return MonoidalStructures(endofunctors)(tensor, unit, comparison(left, right), comparison(left_unit, identity), comparison(right_unit, identity))


class _ActionData(NamedTuple):
    action: Functor
    associator: NaturalTransformation
    unitor: NaturalTransformation


class ActionsCategory(Category[[], []]):
    """The discrete category of supplied coherent left actions of M on C."""

    class ObjectType:
        def __init__(self, data: _ActionData) -> None:
            self._action_data = data

        def monoidal_structure(self) -> MonoidalStructuresCategory.ObjectType:
            return self.category()._monoidal

        def underlying_category(self) -> Category:
            return self.action().codomain()

        def action(self) -> Functor:
            return self._action_data.action

        def associator(self) -> NaturalTransformation:
            return self._action_data.associator

        def unitor(self) -> NaturalTransformation:
            return self._action_data.unitor

        def pentagon(self, m: CategoryOfCategories.ElementType, n: CategoryOfCategories.ElementType, p: CategoryOfCategories.ElementType, x: CategoryOfCategories.ElementType) -> Proposition:
            monoidal, action = self.monoidal_structure(), self.action()
            tensor = monoidal.tensor()
            triples = self.associator().domain().domain()
            a = lambda first, second, value: self.associator().component(triples((first, second, value)))
            mn, np = tensor_object(tensor, m, n), tensor_object(tensor, n, p)
            px = tensor_object(action, p, x)
            alpha = monoidal.associator().component(monoidal.associator().domain().domain()((m, n, p)))
            identity_m = Mor(monoidal.underlying_category())(m, m).one()
            identity_x = Mor(self.underlying_category())(x, x).one()
            return a(m, n, px) * a(mn, p, x) == tensor_morphism(action, identity_m, a(n, p, x)) * a(m, np, x) * tensor_morphism(action, alpha, identity_x)

        def triangle(self, m: CategoryOfCategories.ElementType, x: CategoryOfCategories.ElementType) -> Proposition:
            monoidal, action = self.monoidal_structure(), self.action()
            associator = self.associator().component(self.associator().domain().domain()((m, monoidal.unit(), x)))
            identity_m = Mor(monoidal.underlying_category())(m, m).one()
            identity_x = Mor(self.underlying_category())(x, x).one()
            return tensor_morphism(action, identity_m, self.unitor().component(x)) * associator == tensor_morphism(action, monoidal.right_unitor().component(m), identity_x)

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, monoidal: MonoidalStructuresCategory.ObjectType, base: Category) -> None:
        self._monoidal, self._base = monoidal, base

    def __call__(self, action: Functor, associator: NaturalTransformation, unitor: NaturalTransformation) -> ActionsCategory.ObjectType:
        monoidal = self._monoidal
        assert action in Fun(Cat().Products()((monoidal.underlying_category(), self._base)), self._base)
        triples = Cat().Products()((monoidal.underlying_category(), monoidal.underlying_category(), self._base))
        first, second, third = (triples.product_projection(index) for index in range(3))
        left = action * pair_maps(Cat(), monoidal.tensor() * pair_maps(Cat(), first, second), third)
        right = action * pair_maps(Cat(), first, action * pair_maps(Cat(), second, third))
        identity = Fun(self._base, self._base).one()
        constant = Fun(self._base, monoidal.underlying_category()).constant(monoidal.unit())
        unital = action * pair_maps(Cat(), constant, identity)
        assert associator in Mor(Fun(triples, self._base))(left, right).Isomorphisms()
        assert unitor in Mor(Fun(self._base, self._base))(unital, identity).Isomorphisms()
        return self.ObjectType(_ActionData(action, associator, unitor))

    def construct_morphism(self, source: ActionsCategory.ObjectType, target: ActionsCategory.ObjectType) -> ActionsCategory.MorphismType:
        assert source is target, "a morphism in this discrete category is an identity"
        return self.MorphismType(domain=source, codomain=target)


@cached_function(key=identity_key)
def Actions(monoidal: MonoidalStructuresCategory.ObjectType, base: Category) -> ActionsCategory:
    return ActionsCategory(monoidal, base)


@cached_function(key=identity_key)
def SelfAction(monoidal: MonoidalStructuresCategory.ObjectType) -> ActionsCategory.ObjectType:
    return Actions(monoidal, monoidal.underlying_category())(monoidal.tensor(), monoidal.associator(), monoidal.left_unitor())


@cached_function(key=identity_key)
def TrivialAction(monoidal: MonoidalStructuresCategory.ObjectType, base: Category) -> ActionsCategory.ObjectType:
    """The action through the second projection, with identity coherence maps."""
    pairs = Cat().Products()((monoidal.underlying_category(), base))
    action = pairs.product_projection(1)
    triples = Cat().Products()((monoidal.underlying_category(), monoidal.underlying_category(), base))
    first, second, third = (triples.product_projection(index) for index in range(3))
    left = action * pair_maps(Cat(), monoidal.tensor() * pair_maps(Cat(), first, second), third)
    right = action * pair_maps(Cat(), first, action * pair_maps(Cat(), second, third))
    identity = Fun(base, base).one()
    constant = Fun(base, monoidal.underlying_category()).constant(monoidal.unit())
    unital = action * pair_maps(Cat(), constant, identity)
    associator = natural_isomorphism(left, right,
        lambda triple: Mor(base)(triple.component(2), triple.component(2)).one(),
        lambda triple: Mor(base)(triple.component(2), triple.component(2)).one())
    unitor = natural_isomorphism(unital, identity,
        lambda value: Mor(base)(value, value).one(),
        lambda value: Mor(base)(value, value).one())
    return Actions(monoidal, base)(action, associator, unitor)
