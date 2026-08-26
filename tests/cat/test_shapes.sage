"""The diagram shapes ``Discrete(S)``, ``Thin(P, leq)``, and ``Cat()(labels, generators, relations)``.

Oracles: the definition of the discrete category on a set (objects the points,
identities only; Mathlib ``CategoryTheory.Discrete``), of the thin category of a
preorder (at most one morphism ``x -> y``, present exactly when ``x <= y``; Mathlib
``Preorder.smallCategory``), and of a finitely presented category (D15, D16).
"""

import pytest

from sage_categories.all import *


def _integers():
    """The Python integers by rule, never enumerated."""
    return Sets()(lambda datum: type(datum) is int)


def test_the_discrete_category_on_a_set_has_the_points_as_objects_and_identities_only() -> None:
    three = Sets().Simplex(int(2))
    shape = Discrete(three)
    one, one_again, two = shape(three.point(int(1))), shape(three.point(int(1))), shape(three.point(int(2)))

    assert shape in Cat()
    assert one in shape
    assert three.point(int(1)) is three.point(int(1))
    assert one is one_again
    assert ask(one == one_again) is True
    assert ask(one == two) is False
    assert ask(Mor(shape)(one, one_again)() == one.identity()) is True
    assert one.identity() in Mor(shape)(one, one)
    assert one.identity().inverse() is one.identity()
    assert Sets().identity().inverse() is Sets().identity()
    with pytest.raises(AssertionError):
        Mor(shape)(one, two)()

    integers = _integers()
    seven = Discrete(integers)(integers.point(int(7)))
    assert seven in Discrete(integers)
    assert Discrete(integers)(integers.point(int(7))) is seven
    assert ask(seven.point() == integers.point(int(7))) is True


def test_discrete_is_a_functor_from_sets_to_cat() -> None:
    three, integers = Sets().Simplex(int(2)), _integers()
    times_ten = Mor(Sets())(three, integers)(lambda datum: int(10) * datum)

    assert Discrete in Fun(Sets(), Cat())
    functor = Discrete(times_ten)
    assert functor in Fun(Discrete(three), Discrete(integers))
    vertex = Discrete(three)(three.point(int(2)))
    assert ask(functor.on_object(vertex).point() == integers.point(int(20))) is True
    assert functor.on_morphism(vertex.identity()) in Mor(Discrete(integers))
    assert ask(functor.on_morphism(vertex.identity()).domain() == Discrete(integers)(integers.point(int(20)))) is True


def test_the_thin_category_of_a_preorder_has_one_comparison_per_related_pair() -> None:
    three = Sets().Simplex(int(2))
    points = list(three)

    def position(point):
        return next(index for index, candidate in enumerate(points) if ask(candidate == point) is True)

    leq = Predicate("leq", int(2), True)
    leq.register_handler(lambda first, second: position(first) <= position(second))
    thin = Thin(three, leq)
    zero, one, two = (thin(three.point(int(k))) for k in range(int(3)))

    zero_to_one, one_to_two = Mor(thin)(zero, one)(), Mor(thin)(one, two)()
    assert zero_to_one in Mor(thin)(zero, one)
    assert ask(one_to_two * zero_to_one == Mor(thin)(zero, two)()) is True
    assert ask(Mor(thin)(one, one)() == one.identity()) is True
    with pytest.raises(AssertionError):
        Mor(thin)(two, zero)()


def test_a_comparison_with_an_undecided_order_has_unknown_membership() -> None:
    integers = _integers()
    divides = Predicate("divides", int(2), True)
    thin = Thin(integers, divides)
    two, six = thin(integers.point(int(2))), thin(integers.point(int(6)))

    comparison = Mor(thin)(two, six)()
    assert ask(Mor(thin).membership_proposition(comparison)) is Unknown
    assert comparison not in Mor(thin)
    assume(divides(two.point(), six.point()))
    assert comparison in Mor(thin)


def test_the_uniform_call_form_constructs_a_presented_shape_with_its_relations() -> None:
    triangle = Cat()((int(0), int(1), int(2)), (("u", int(0), int(1)), ("v", int(1), int(2)), ("w", int(0), int(2))), ((("u", "v"), ("w",)),))

    assert triangle in Cat()
    assert triangle.generator("u") in Mor(triangle)(triangle(int(0)), triangle(int(1)))
    assert ask(triangle.generator("v") * triangle.generator("u") == triangle.generator("w")) is True
    assert ask(triangle.generator("w") == triangle(int(0)).identity()) is False

    retraction = Cat()((int(0), int(1)), (("s", int(0), int(1)), ("r", int(1), int(0))), ((("s", "r"), ()),))
    assert ask(retraction.generator("r") * retraction.generator("s") == retraction(int(0)).identity()) is True
    assert retraction.generator("s") not in Mor(retraction).Isomorphisms()
    assert retraction.generator("r") not in Mor(retraction).Isomorphisms()
    walking = Cat().WalkingIsomorphism()
    assert walking.generator("f") in Mor(walking).Isomorphisms()
