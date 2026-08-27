"""Construction categories, operators, ``Cat()``'s owned constructions, and evaluation functors.

Oracles: the definitions of the product and coproduct of categories (Mathlib
``CategoryTheory.pi``, ``CategoryTheory.Sigma.sigma``), of the strict pullback of
categories (POL-CAT-050), of the exponential ``Fun(C, D)`` (Mathlib ``Cat.exp_obj``), of
the evaluation functors of ``Fun(I, C)`` (POL-FUN-029), and of the presentation data every
construction retains (POL-CAT-046, POL-FUN-009/010).  No row proves a universal
property (POL-MATH-036, POL-TEST-006).
"""

import pytest

from sage_categories.all import *
from sage_categories.cat.constructions import cone, vertex_of
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory


class Bare(Category):
    """A category with three empty role declarations and no owned constructions."""

    class DeclaredObjectType(ObjectOfCategory):
        """No local operation."""

    class DeclaredElementType(ElementOfObject):
        """No local operation."""

    class DeclaredMorphismType(MorphismOfCategory):
        """No local operation."""

    def __repr__(self):
        return "Bare"


def _fold(images, path):
    """The image of a path under generator images, composed in the order of the word."""
    if not path.word():
        return images["identity"](path.domain())
    first, *rest = path.word()
    image = images[first]
    for name in rest:
        image = images[name] * image
    return image


def _cospan_diagram(first_functor, second_functor):
    """The diagram ``L(2, 2) -> Cat()`` with the two functors as its legs."""
    cospan = Cat().Horn(int(2), int(2))
    objects = {int(0): first_functor.domain(), int(1): second_functor.domain(), int(2): first_functor.codomain()}
    images = {"identity": lambda vertex: objects[cospan.label(vertex)].identity(), "0->2": first_functor, "1->2": second_functor}
    return Fun(cospan, Cat())(lambda vertex: objects[cospan.label(vertex)], lambda path: _fold(images, path))


def _point_functor(category, member_object):
    return Fun(Cat().Terminal(), category)(lambda vertex: member_object, lambda path: member_object.identity())


def test_operators_are_the_binary_construction_categories() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    assert two * three is Sets().Products()((two, three))
    assert two + three is Sets().Coproducts()((two, three))
    assert (two * three).diagram() is (two + three).diagram()
    assert Sets() * Cat() is Cat().Products()((Sets(), Cat()))
    assert Sets() + Cat() is Cat().Coproducts()((Sets(), Cat()))
    assert Cat() ** Sets() is Fun(Sets(), Cat())
    assert (Sets() * Cat())((two, Sets())) in (Sets() * Cat())
    with pytest.raises(AssertionError):
        two * Cat()
    with pytest.raises(AssertionError):
        two @ three


def test_a_category_product_has_projections_with_exact_endpoints_acting_componentwise() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    arrow = Cat().Simplex(int(1))
    product = Cat().Products()((arrow, Sets()))
    first, second = product.product_projection(int(0)), product.product_projection(int(1))

    assert product in Cat().Products()
    assert product.category().category() is Cat()
    assert first in Fun(product, arrow)
    assert first.domain() is product and first.codomain() is arrow
    assert second.codomain() is Sets()
    assert first is not second

    pair = product((arrow(int(0)), two))
    other = product((arrow(int(1)), three))
    assert first.on_object(pair) is arrow(int(0))
    assert second.on_object(pair) is two
    morphism = Mor(product)(pair, other)((arrow.generator("0->1"), successor))
    assert ask(first.on_morphism(morphism) == arrow.generator("0->1"))
    assert second.on_morphism(morphism) is successor

    generalized = product.element_from_defining_morphism(morphism)
    assert generalized.defining_morphism().domain() is pair and generalized.parent() is other
    image = first.on_element(generalized)
    assert ask(image.defining_morphism() == arrow.generator("0->1"))
    assert image.defining_morphism().domain() is arrow(int(0)) and image.parent() is arrow(int(1))


def test_a_category_coproduct_has_injections_that_tag() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    coproduct = Cat().Coproducts()((Sets(), Cat()))
    into_sets, into_cat = coproduct.coproduct_injection(int(0)), coproduct.coproduct_injection(int(1))

    assert into_sets in Fun(Sets(), coproduct)
    assert into_cat.domain() is Cat() and into_cat.codomain() is coproduct
    tagged = into_sets.on_object(two)
    assert tagged in coproduct
    assert tagged.member() is two
    assert into_sets.on_morphism(successor).morphism() is successor
    assert into_sets.on_morphism(successor).domain() is tagged
    # An object of the coproduct is the pair ``(i, X)`` (Mathlib
    # ``CategoryTheory.Sigma.sigma``), so two objects with different tags are distinct
    # and two with one tag are distinct exactly when their members are.
    assert not ask(tagged == into_cat.on_object(Sets()))
    assert not ask(tagged == into_sets.on_object(three))
    with pytest.raises(AssertionError):
        Mor(coproduct)(tagged, into_cat.on_object(Sets()))(successor)

    # A generalized point follows the injection's morphism action.
    generalized = Sets().element_from_defining_morphism(successor)
    image = into_sets.on_element(generalized)
    assert image.defining_morphism().domain() is tagged
    assert image.parent() is into_sets.on_object(three)
    assert image.defining_morphism().morphism() is successor


def test_a_universal_construction_has_one_apex_and_one_defining_morphism_each() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))

    product = Cat().Products()((Sets(), Cat()))
    coproduct = Cat().Coproducts()((Sets(), Cat()))
    assert Cat().Products()((Sets(), Cat())) is product
    assert Cat().Coproducts()((Sets(), Cat())) is coproduct

    projection = product.product_projection(int(0))
    injection = coproduct.coproduct_injection(int(0))
    assert product.product_projection(int(0)) is projection
    assert coproduct.coproduct_injection(int(0)) is injection

    assert injection.on_object(two) is injection.on_object(two)
    assert injection.on_morphism(successor) is injection.on_morphism(successor)
    assert ask(injection.on_morphism(successor) == injection.on_morphism(successor))
    assert projection.on_object(product((two, Sets()))) is two

    # The set product is the same statement one level down.
    pair = Sets().Products()((two, three))
    assert Sets().Products()((two, three)) is pair
    assert pair.product_projection(int(0)) is pair.product_projection(int(0))
    assert pair.cone().component(vertex_of(pair.diagram().domain(), int(0))) is pair.product_projection(int(0))


def test_the_mediator_of_a_category_cone_lands_in_the_product() -> None:
    two = Sets().Simplex(int(1))
    product = Sets() * Cat()
    point = Cat().Terminal()
    legs = {int(0): _point_functor(Sets(), two), int(1): _point_functor(Cat(), Sets())}
    index = product.index_category()
    candidate = cone(product.diagram(), point, lambda vertex: legs[int(0)] if ask(vertex.point() == Sets().Simplex(int(1)).point(int(0))) else legs[int(1)])

    mediating = product.universal_morphism(candidate)
    assert mediating in Fun(point, product)
    assert product.product_projection(int(0)).on_object(mediating.on_object(point(int(0)))) is two
    assert product.product_projection(int(1)).on_object(mediating.on_object(point(int(0)))) is Sets()


def test_a_construction_category_exists_without_an_owned_construction() -> None:
    bare = Bare()
    arrow = Cat().Simplex(int(1))
    family = bare.Limits(arrow)
    assert family in Cat()
    assert bare.Limits(Cat().Simplex(int(2))) is not family
    assert bare.Pullbacks() is bare.Limits(Cat().Horn(int(2), int(2)))
    assert bare.Equalizers() is bare.Limits(Cat().WalkingParallelPair())
    with pytest.raises(AssertionError):
        family(Fun(arrow, bare).constant(bare.ObjectType(bare)))

    parallel = Cat().WalkingParallelPair()
    assert Cat().Limits(parallel) in Cat()
    with pytest.raises(AssertionError):
        Cat().Limits(parallel)(Fun(parallel, Cat()).constant(Sets()))


def test_the_strict_pullback_in_cat_admits_identical_images_and_leaves_distinct_rule_defined_images_unknown() -> None:
    point = Cat().Terminal()
    integers, other_integers = Sets()(lambda datum: type(datum) is int), Sets()(lambda datum: type(datum) is int)
    select_integers, select_integers_again = _point_functor(Sets(), integers), _point_functor(Sets(), integers)
    select_other = _point_functor(Sets(), other_integers)

    pullback = Cat().Pullbacks()(_cospan_diagram(select_integers, select_integers_again))
    assert pullback in Cat().Limits(Cat().Horn(int(2), int(2)))
    pair = pullback((point(int(0)), point(int(0))))
    assert pair in pullback
    assert pullback.projection(Cat().Horn(int(2), int(2))(int(0))).on_object(pair) is point(int(0))
    assert pullback.projection(Cat().Horn(int(2), int(2))(int(2))).on_object(pair) is integers

    undecided = Cat().Pullbacks()(_cospan_diagram(select_integers, select_other))
    candidate = undecided((point(int(0)), point(int(0))))
    assert ask(undecided.membership_proposition(candidate)) is Unknown


def test_fun_of_the_walking_arrow_has_morphisms_as_objects_and_evaluations_as_endpoints() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    constant = Mor(Sets())(two, three)(lambda datum: int(0))
    arrow = Cat().Simplex(int(1))
    squares = Fun(arrow, Sets())
    ev_0, ev_1 = squares.evaluation(arrow(int(0))), squares.evaluation(arrow(int(1)))

    assert successor.defining_morphism() in squares
    assert ev_0 in Fun(squares, Sets()) and ev_1 in Fun(squares, Sets())
    assert ev_0.on_object(successor.defining_morphism()) is two
    assert ev_1.on_object(successor.defining_morphism()) is three

    zero = Mor(Sets())(three, three)(lambda datum: int(0))
    components = {int(0): two.identity(), int(1): zero}
    square = Mor(squares)(successor, constant)(lambda vertex: components[arrow.label(vertex)])
    assert square in Mor(squares)
    assert ev_0.on_morphism(square) is two.identity()
    assert ev_1.on_morphism(square) is zero
    assert squares.constant(two).on_morphism(arrow.generator("0->1")) is two.identity()
