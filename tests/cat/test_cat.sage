"""``Cat()``, the ``Mor`` tower, functors, natural transformations, properties, and canonical objects.

Every expected fact has its oracle in the definition it exercises: the bootstrap
convention ``Cat().category() is Cat()`` (POL-CAT-002), the definition of
``Mor(n, C)`` (POL-CAT-021), the definition of a functor's actions (POL-FUN-001)
and of composition of functors and natural transformations, the canonical shapes
(POL-CAT-083), and the functor property implications (POL-FUN-024).  No row
claims to prove a functor law, naturality, or a universal property (POL-MATH-036).
"""

import pytest

from sage_categories.all import *
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory


class Bare(Category):
    """A category with three empty role declarations and no structural graph."""

    class ObjectType(ObjectOfCategory):
        """No local operation."""

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def __repr__(self):
        return "Bare"


def _fold(functor_images, path):
    """The image of a path under generator images, composed in the order of the word."""
    if not path.word():
        return functor_images["identity"](path.domain())
    first, *rest = path.word()
    image = functor_images[first]
    for name in rest:
        image = functor_images[name] * image
    return image


def test_cat_is_unstratified_and_bootstrapped_first() -> None:
    assert Cat().category() is Cat()
    assert Cat() in Cat()
    assert Cat().structure_functors() == ()
    assert Cat().ObjectType is Category


def test_an_ordinary_category_is_an_object_of_cat() -> None:
    bare = Bare()
    assert bare.category() is Cat()
    assert bare in Cat()
    assert Sets().category() is Cat()
    assert Fun.category() is Cat()
    assert Fun(Sets(), Sets()).category() is Cat()


def test_every_category_declares_three_distinct_roles() -> None:
    for category in (Cat(), Sets(), Mor(Sets()), Bare()):
        assert category.ObjectType is not category.ElementType
        assert category.ElementType is not category.MorphismType
        assert category.ObjectType is not category.MorphismType


def test_mor_tower() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))

    assert Mor(int(0), Sets()) is Sets()
    assert Mor(Sets()) is Mor(int(1), Sets())
    assert successor in Mor(int(1), Sets())
    assert successor in Mor(Sets())(two, three)
    assert successor not in Mor(Sets())(three, two)
    assert Mor(Cat()) is Fun
    assert Mor(int(2), Cat()) is Mor(Fun)


def test_a_functor_is_a_morphism_of_cat_and_an_object_of_fun() -> None:
    two = Sets().Simplex(int(1))
    walking_arrow = Cat().Simplex(int(1))
    successor = Mor(Sets())(two, two)(lambda datum: int(1) - datum)
    images = {"identity": lambda vertex: two.identity(), "0->1": successor}

    arrow = Fun(walking_arrow, Sets())(lambda vertex: two, lambda path: _fold(images, path))

    assert arrow in Mor(Cat())
    assert arrow in Fun
    assert arrow in Fun(walking_arrow, Sets())
    assert arrow.on_object(walking_arrow(int(0))) is two
    assert arrow.on_morphism(walking_arrow.generator("0->1")) is successor
    assert ask(arrow.on_morphism(walking_arrow(int(1)).identity()) == two.identity()) is True


def test_fixed_endpoints() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    assert Fun(Sets(), Sets()) is Mor(Cat())(Sets(), Sets())

    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    constant = Mor(Sets())(two, three)(lambda datum: int(0))
    two_cells = Mor(Mor(Sets())(two, three))
    assert two_cells(successor, successor).identity() in two_cells(successor, successor)
    assert two_cells(successor, successor).identity() not in two_cells(successor, constant)


def test_natural_transformations_compose_componentwise() -> None:
    point = Cat().Terminal()
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    constant_two = Fun(point, Sets())(lambda vertex: two, lambda path: two.identity())
    constant_three = Fun(point, Sets())(lambda vertex: three, lambda path: three.identity())
    constant_four = Fun(point, Sets())(lambda vertex: four, lambda path: four.identity())
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    successor_again = Mor(Sets())(three, four)(lambda datum: datum + int(1))

    eta = Mor(Fun(point, Sets()))(constant_two, constant_three)(lambda vertex: successor)
    theta = Mor(Fun(point, Sets()))(constant_three, constant_four)(lambda vertex: successor_again)

    assert eta in Mor(Fun(point, Sets()))
    assert eta in Mor(Fun)
    assert eta.component(point(int(0))) is successor
    composite = theta * eta
    add_two = Mor(Sets())(two, four)(lambda datum: datum + int(2))
    assert ask(composite.component(point(int(0))) == add_two) is True


def test_canonical_objects_exist_by_identity() -> None:
    assert Cat().Simplex(int(1)) is Cat().Simplex(int(1))
    assert Cat().Terminal() is Cat().Simplex(int(0))
    assert Cat().Horn(int(2), int(1)) is Cat().Simplex(int(2))
    assert Cat().Horn(int(2), int(2)) is Cat().Horn(int(2), int(2))
    assert Sets().Terminal() is Sets().classical_stages()[int(0)]

    span, cospan = Cat().Horn(int(2), int(0)), Cat().Horn(int(2), int(2))
    assert span.generator("0->1") in Mor(span)(span(int(0)), span(int(1)))
    assert span.generator("0->2") in Mor(span)(span(int(0)), span(int(2)))
    assert cospan.generator("1->2") in Mor(cospan)(cospan(int(1)), cospan(int(2)))
    composite = Cat().Simplex(int(2)).generator("1->2") * Cat().Simplex(int(2)).generator("0->1")
    assert ask(composite == Mor(Cat().Simplex(int(2)))(Cat().Simplex(int(2))(int(0)), Cat().Simplex(int(2))(int(2)))(("0->1", "1->2"))) is True

    two = Sets().Simplex(int(1))
    swap = Mor(Sets())(two, two)(lambda datum: int(1) - datum)
    arrow = swap.defining_morphism()
    assert arrow in Fun(Cat().Simplex(int(1)), Sets())
    assert arrow.on_morphism(Cat().Simplex(int(1)).generator("0->1")) is swap
    assert swap.defining_morphism() is arrow
    assert two.defining_morphism().on_object(Cat().Terminal()(int(0))) is two

    vertex, edge = Cat().element_from_defining_morphism(two.defining_morphism()), Cat().element_from_defining_morphism(arrow)
    assert vertex.stage() is Cat().Terminal() and vertex.parent() is Sets().Finite()
    assert edge.stage() is Cat().Simplex(int(1)) and edge.parent() is Sets()
    assert vertex.defining_morphism().on_object(Cat().Terminal()(int(0))) is two
    assert edge.defining_morphism().on_morphism(Cat().Simplex(int(1)).generator("0->1")) is swap


def test_global_and_fixed_endpoint_property_dispatch_reach_one_category() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    assert Fun.Full()(Sets(), Sets()) is Fun(Sets(), Sets()).Full()
    assert Fun.Faithful()(Sets(), Sets()) is Fun(Sets(), Sets()).Faithful()
    assert Fun.FullyFaithful()(Sets(), Sets()) is Fun(Sets(), Sets()).FullyFaithful()
    assert Mor(Sets()).Monomorphisms()(two, three) is Mor(Sets())(two, three).Monomorphisms()


def test_property_methods_return_applied_predicates() -> None:
    identity = Fun(Sets(), Sets())(lambda member: member, lambda morphism: morphism)
    proposition = identity.is_full()
    assert proposition.arguments()[int(0)] is identity
    with pytest.raises(TypeError):
        bool(proposition)
    two = Sets().Simplex(int(1))
    swap = Mor(Sets())(two, two)(lambda datum: int(1) - datum)
    assert swap.is_monomorphism().arguments()[int(0)] is swap


def test_direct_construction_and_assumption_refine_the_same_functor() -> None:
    assumed = Fun(Sets(), Sets())(lambda member: member, lambda morphism: morphism)
    assume(assumed.is_full())
    assert assumed in Fun.Full()
    assert ask(assumed.is_full()) is True

    constructed = Fun(Sets(), Sets())(lambda member: member, lambda morphism: morphism)
    assert Fun(Sets(), Sets()).Faithful()(constructed) is constructed
    assert constructed in Fun.Faithful()
    assert constructed in Fun(Sets(), Sets()).Faithful()


def test_an_unplaced_functor_property_is_unknown() -> None:
    functor = Fun(Sets(), Sets())(lambda member: member, lambda morphism: morphism)
    assert ask(functor.is_essentially_surjective()) is Unknown
    assert ask(functor.is_full()) is Unknown
    assert functor not in Fun.Full()


def test_full_faithfulness_implies_fullness_and_faithfulness() -> None:
    functor = Fun(Sets(), Sets()).FullyFaithful()(lambda member: member, lambda morphism: morphism)
    assert ask(functor.is_full()) is True
    assert ask(functor.is_faithful()) is True
    assert functor in Fun.Faithful()
    assert ask(functor.is_essentially_surjective()) is Unknown


def test_a_constructed_functor_maps_one_nonidentity_composite() -> None:
    triangle = Cat().Simplex(int(2))
    one, two, three = Sets().Simplex(int(0)), Sets().Simplex(int(1)), Sets().Simplex(int(2))
    include = Mor(Sets())(one, two)(lambda datum: datum)
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    objects = {int(0): one, int(1): two, int(2): three}
    images = {"identity": lambda vertex: objects[triangle.label(vertex)].identity(), "0->1": include, "1->2": successor}

    functor = Fun(triangle, Sets())(lambda vertex: objects[triangle.label(vertex)], lambda path: _fold(images, path))

    composite = triangle.generator("1->2") * triangle.generator("0->1")
    assert ask(functor.on_morphism(composite) == successor * include) is True
    assert ask(functor.on_morphism(composite)(one.point(int(0))) == three.point(int(1))) is True


def test_generic_identity_and_composition() -> None:
    walking = Cat().WalkingIsomorphism()
    two, pair = Sets().Simplex(int(1)), Sets().Finite()((int(10), int(20)))
    swap = Mor(Sets())(two, pair).Isomorphisms()(lambda datum: int(10) * (datum + int(1)), lambda datum: datum // int(10) - int(1))
    objects = {int(0): two, int(1): pair}
    images = {"identity": lambda vertex: objects[walking.label(vertex)].identity(), "f": swap, "g": swap.inverse()}
    functor = Fun(walking, Sets())(lambda vertex: objects[walking.label(vertex)], lambda path: _fold(images, path))
    identity = Fun(Sets(), Sets()).Equivalences().identity()
    composite = identity * functor

    assert identity.on_object(two) is two
    assert identity.on_morphism(swap) is swap
    assert ask(identity.is_equivalence()) is True
    assert composite.on_object(walking(int(1))) is pair
    assert composite.on_morphism(walking.generator("f")) is swap

    inverse_image = functor.on_morphism(walking.generator("f").inverse())
    assert inverse_image is functor.on_morphism(walking.generator("f")).inverse()
    assert ask(inverse_image(pair.point(int(20))) == two.point(int(1))) is True


def test_the_induced_element_action_follows_the_morphism_action() -> None:
    walking_arrow = Cat().Simplex(int(1))
    one, two = Sets().Terminal(), Sets().Simplex(int(1))
    select_one = Mor(Sets())(one, two)(lambda star: int(1))
    objects = {int(0): one, int(1): two}
    images = {"identity": lambda vertex: objects[walking_arrow.label(vertex)].identity(), "0->1": select_one}
    functor = Fun(walking_arrow, Sets())(lambda vertex: objects[walking_arrow.label(vertex)], lambda path: _fold(images, path))
    composite = Fun(Sets(), Sets()).Equivalences().identity() * functor

    generalized = walking_arrow.element_from_defining_morphism(walking_arrow.generator("0->1"))
    assert generalized.stage() is walking_arrow(int(0))
    assert generalized.parent() is walking_arrow(int(1))

    image = functor.on_element(generalized)
    assert image.parent() is two
    assert image.stage() is one
    assert image.defining_morphism() is select_one
    assert ask(image == two.point(int(1))) is True
    assert composite.on_element(generalized).defining_morphism() is select_one


def test_equality_is_a_predicate_decided_by_ask() -> None:
    four = Sets().Simplex(int(3))
    first, second, first_again = four.point(int(1)), four.point(int(2)), four.point(int(1))

    assert ask(first == second) is False
    assert ask(first == first_again) is True
    assert ask(first != second) is True
    assert hash(first) == hash(first_again)
    with pytest.raises(TypeError):
        bool(first == second)
    with pytest.raises(TypeError):
        bool(four == four)
    assert ask(four == four) is True
