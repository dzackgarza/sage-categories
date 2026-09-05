"""Public consumers of inherited properties and categorical constructions."""

from __future__ import annotations

import pytest

from sage_categories.all import Cat, Category, Fun, Mor, Predicate, Unknown, ask, assume
from sage_categories.cat.category import Axiom
from sage_categories.cat.predicates import Proposition, Query
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.cat.cones import cone, cones, cocone, cocones
from sage_categories.cat.diagrams import cospan_diagram, from_sequence
from sage_categories.kernel.compiler import SemanticCollisionError


class Nonnegative(Predicate):
    name = "nonnegative"


nonnegative = Nonnegative()


class Scalars(Category):
    class ObjectType:
        def __init__(self, value: int) -> None:
            self._scalar = value

        def scalar(self) -> int:
            return self._scalar

    class ElementType:
        pass

    class MorphismType:
        pass

    def _positive(self, value: Scalars.ObjectType) -> Proposition:
        return nonnegative(value)

    Positive = Axiom(_positive)

    def __call__(self, value: int) -> Scalars.ObjectType:
        return self.ObjectType(value)


def decide_nonnegative(value: Scalars.ObjectType, assumptions: Proposition) -> bool | None:
    return value.scalar() >= 0


nonnegative.register_handler(decide_nonnegative)


class PositiveScalars(PropertySubcategory):
    _base_category_class_and_axiom = (Scalars, "Positive")

    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    Strict = Axiom()


class Decorated(Category):
    class ObjectType:
        def __init__(self, value: int) -> None:
            self._decoration = value

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, first: Scalars, second: Scalars) -> None:
        self._first = first
        self._second = second

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        def into(target: Scalars) -> Cat().MorphismType:
            return Fun(self, target).Isofibrations()(
                lambda value: target(value._decoration),
                lambda arrow: Mor(target)(target(arrow.domain()._decoration), target(arrow.codomain()._decoration)).one(),
            )
        return (into(self._first), into(self._second))

    def __call__(self, value: int) -> Decorated.ObjectType:
        return self.ObjectType(value)


class ScalarPair(Category):
    class ObjectType:
        def __init__(self, values: tuple[int, int]) -> None:
            self._coordinates = values

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, first: Scalars, second: Scalars, reverse: bool) -> None:
        self._scalar_targets = (first, second)
        self._reverse = reverse

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        projections = tuple(
            Fun(self, target).Isofibrations()(
                lambda value, index=index, target=target: target(value._coordinates[index]),
                lambda arrow, index=index, target=target: Mor(target)(target(arrow.domain()._coordinates[index]), target(arrow.codomain()._coordinates[index])).one(),
            )
            for index, target in enumerate(self._scalar_targets)
        )
        return projections[::-1] if self._reverse else projections

    def __call__(self, values: tuple[int, int]) -> ScalarPair.ObjectType:
        return self.ObjectType(values)


def test_selected_initialization_order_is_local_to_each_declaration() -> None:
    for orders in ((False, True), (True, False)):
        first, second = Scalars(), Scalars()
        declarations = [ScalarPair(first, second, order) for order in orders]
        for category, reverse in zip(declarations, orders):
            assert category((3, 5)).scalar() == (5 if reverse else 3)
            category.recompile()
            assert category((7, 11)).scalar() == (11 if reverse else 7)


def test_an_axiom_declared_on_a_property_retains_its_owner() -> None:
    category = Scalars()
    strict = category.Positive().Strict()
    value = strict(3)
    assert ask(value.is_strict()) is True
    assert value.is_strict() == strict.membership_proposition(value)


def test_typed_queries_return_owned_answers_and_defer_comparisons() -> None:
    result = Cat().Simplex(1)
    query = Query("classification", 1, result)

    def classify(value: Scalars.ObjectType) -> Cat().Simplex(1).ObjectType:
        return result(1)

    query.register_handler(classify)
    value = Scalars()(3)
    assert ask(query(value)) is result(1)
    assert ask(query(value) == result(1)) is True
    assert ask(query(value) == result(0)) is False
    assert ask(query(Cat().Terminal()(0))) is Unknown


def test_unrelated_state_owners_are_distinct_even_for_equal_values() -> None:
    class Independent(Category):
        class ObjectType:
            def __init__(self, value: int) -> None:
                self._scalar = value

        class ElementType:
            pass

        class MorphismType:
            pass

        def __call__(self, value: int) -> Independent.ObjectType:
            return self.ObjectType(value)

    first, second = Scalars(), Independent()

    class Combined(Category):
        class ObjectType:
            pass

        class ElementType:
            pass

        class MorphismType:
            pass

        def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
            return tuple(
                Fun(self, target).Isofibrations()(
                    lambda value, target=target: target(0),
                    lambda arrow, target=target: Mor(target)(target(0), target(0)).one(),
                )
                for target in (first, second)
            )

        def __call__(self) -> Combined.ObjectType:
            return self.ObjectType(None)

    category = Combined()
    with pytest.raises(SemanticCollisionError, match="_scalar"):
        category()


def test_two_selected_targets_supply_one_inherited_property() -> None:
    first, second = Scalars(), Scalars()
    source = Decorated(first, second)
    positive = source.Positive()
    value = positive(3)
    assert value.scalar() == 3
    assert value.category() is positive
    assert ask(value.is_positive()) is True
    for functor, target in zip(source.selected_functors(), (first, second)):
        assert functor.inverse_image(target.Positive()) is positive
        diagram = cospan_diagram(Cat(), functor, target.Positive().subcategory_monomorphism())
        presentation = Cat().Pullbacks().universal_data(diagram)
        assert presentation.apex() is positive
        assert presentation.leg(0).on_object(value) is value
        assert presentation.leg(1).on_object(value) is functor.on_object(value)
        assert presentation.leg(1).on_object(value) in target.Positive()


def test_product_elements_and_universal_functor_actions() -> None:
    first, second = Cat().Simplex(1), Cat().Simplex(2)
    product = Cat().Products()(first, second)
    value = product(first(0), second(1))
    assert product.product_projection(0).on_object(value) is first(0)
    assert product.product_projection(1).on_object(value) is second(1)
    diagram = from_sequence(Cat(), (first, second))
    presentation = Cat().Limits(diagram.domain()).universal_data(diagram)
    walking_arrow = Cat().Simplex(1)
    first_map = Fun(first, first).one()
    second_map = Fun(walking_arrow, second)(
        lambda vertex: second(walking_arrow.label(vertex)),
        lambda arrow: Mor(second)(second(walking_arrow.label(arrow.domain())), second(walking_arrow.label(arrow.codomain())))(arrow.word()),
    )
    candidate = cones(diagram)(cone(diagram, walking_arrow, lambda vertex: (first_map, second_map)[diagram.domain().label(vertex)]))
    mediator = presentation.lift(candidate)
    arrow = walking_arrow.generator("0->1")
    image = mediator.on_morphism(arrow)
    assert image.domain() is mediator.on_object(arrow.domain())
    assert image.codomain() is mediator.on_object(arrow.codomain())
    assert product.product_projection(0).on_morphism(image) is arrow
    assert product.product_projection(1).on_morphism(image) is second_map.on_morphism(arrow)


def test_coproduct_presentation_retains_the_original_diagram() -> None:
    first, second = Cat().Simplex(1), Cat().Simplex(2)
    coproduct = Cat().Coproducts()(first, second)
    diagram = from_sequence(Cat(), (first, second))
    presentation = Cat().Colimits(diagram.domain()).universal_data(diagram)
    assert presentation.diagram() is diagram
    assert coproduct.index_category() is diagram.domain()
    assert presentation.leg(0) is coproduct.coproduct_injection(0)
    assert presentation.leg(1) is coproduct.coproduct_injection(1)
    target = Cat().Terminal()
    maps = (Fun(first, target).constant(target(0)), Fun(second, target).constant(target(0)))
    candidate = cocones(diagram)(cocone(diagram, target, lambda vertex: maps[diagram.domain().label(vertex)]))
    mediator = presentation.lift(candidate)
    for index, summand in enumerate((first, second)):
        injection = presentation.leg(index)
        assert mediator.on_object(injection.on_object(summand(0))) is target(0)
        arrow = summand.generator("0->1")
        assert mediator.on_morphism(injection.on_morphism(arrow)) is Mor(target)(target(0), target(0)).one()


def test_images_requested_after_the_functor_action_recognize_the_retained_values() -> None:
    category = Cat().Simplex(1)
    functor = Fun(category, category).one()
    value = functor.on_object(category(0))
    arrow = functor.on_morphism(category.generator("0->1"))
    for image in (category.StrictImage(functor), category.FullImage(functor), category.EssentialImage(functor)):
        assert value in image
        assert arrow in Mor(image)
        assert functor.on_object(category(0)) is value
        assert functor.on_morphism(category.generator("0->1")) is arrow
        assert value in image


for name, value in tuple(globals().items()):
    if name.startswith("test_"):
        value()
