"""Comma categories, pointwise limits in ``Fun(I, C)``, and Kan extensions in ``Sets()``.

Oracles: the comma category ``(K, d)`` has as objects the pairs ``(c, K c -> d)``
(Mathlib ``CategoryTheory.Comma``, ``CostructuredArrow``); the left Kan extension of
``F: [1] -> Sets()`` along the inclusion ``K: [1] -> [2]`` is computed pointwise as
``(Lan_K F)(d) = colim_{(K, d)} F`` (Mathlib ``Functor.pointwiseLeftKanExtension``),
so ``(Lan_K F)(2)`` is the colimit of ``F(0) -> F(1)`` over the arrow-shaped comma
``(K, 2)``, a set of ``#F(1)`` classes, and ``(Ran_K F)(2)`` is the limit over the
empty comma ``(2, K)``, a one-point set; limits in ``Fun(I, C)`` are computed
pointwise (Mathlib ``Limits.evaluationJointlyReflectsLimits``).  No row proves a
universal property (POL-MATH-036).
"""

from sage_categories.all import *
from sage_categories.cat.kan import left_kan_extension, left_kan_unit, right_kan_counit, right_kan_extension
from sage_categories.cat.slices import comma_category


def _path_functor(source, target, label_map):
    """The functor between simplex categories sending vertex ``i`` to ``label_map(i)`` and a path to the path between the images."""
    return Fun(source, target)(
        lambda vertex: target(label_map(source.label(vertex))),
        lambda path: target.construct_morphism(
            target(label_map(source.label(path.domain()))),
            target(label_map(source.label(path.codomain()))),
            tuple(f"{label_map(k)}->{label_map(k) + int(1)}" for k in range(source.label(path.domain()), source.label(path.codomain()))),
        ),
    )


def _arrow_diagram(two, three, successor):
    arrow = Cat().Simplex(int(1))
    objects = {int(0): two, int(1): three}
    return Fun(arrow, Sets())(lambda vertex: objects[arrow.label(vertex)], lambda path: objects[arrow.label(path.domain())].identity() if not path.word() else successor)


def test_the_comma_category_is_the_pullback_of_the_endpoint_functor_with_the_expected_objects() -> None:
    arrow, triangle = Cat().Simplex(int(1)), Cat().Simplex(int(2))
    inclusion = _path_functor(arrow, triangle, lambda label: label)
    comma = comma_category(inclusion, triangle.point_functor(triangle(int(2))))

    assert comma in Cat()
    assert comma_category(inclusion, triangle.point_functor(triangle(int(2)))) is comma
    assert comma.second_functor().domain() is Fun(arrow, triangle)
    assert comma.first_functor().codomain() is Cat().Products()((triangle, triangle)).apex()
    objects = list(comma.object_set())
    assert ask(comma.object_set().cardinality() == int(2)) is True
    structures = [comma.object_at(point).second() for point in objects]
    assert any(ask(structure == triangle.generator("1->2")) is True for structure in structures)
    assert any(ask(structure == triangle.generator("1->2") * triangle.generator("0->1")) is True for structure in structures)
    assert len(comma.generating_morphisms()) == int(3)
    assert ask(comma_category(inclusion, triangle.point_functor(triangle(int(0)))).object_set().cardinality() == int(1)) is True


def test_the_left_kan_extension_retains_its_unit_and_applies_a_nonidentity_component() -> None:
    arrow, triangle = Cat().Simplex(int(1)), Cat().Simplex(int(2))
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    inclusion = _path_functor(arrow, triangle, lambda label: label)
    diagram = _arrow_diagram(two, three, successor)

    extension = left_kan_extension(inclusion, diagram)
    assert extension in Fun(triangle, Sets())
    assert left_kan_extension(inclusion, diagram) is extension
    assert ask(extension.on_object(triangle(int(0))).cardinality() == int(2)) is True
    assert ask(extension.on_object(triangle(int(1))).cardinality() == int(3)) is True
    assert ask(extension.on_object(triangle(int(2))).cardinality() == int(3)) is True

    unit = left_kan_unit(inclusion, diagram)
    assert unit in Mor(Fun(arrow, Sets()))
    assert unit.domain() is diagram
    restricted = unit.codomain()
    assert restricted in Fun(arrow, Sets())
    assert restricted.on_object(arrow(int(1))) is extension.on_object(inclusion.on_object(arrow(int(1))))
    assert ask(restricted.on_morphism(arrow.generator("0->1")) == extension.on_morphism(inclusion.on_morphism(arrow.generator("0->1")))) is True
    component = unit.component(arrow(int(1)))
    assert component.domain() is three and component.codomain() is extension.on_object(triangle(int(1)))
    assert component is not three.identity()
    image = component(three.point(int(2)))
    assert image in extension.on_object(triangle(int(1)))
    assert ask(image == component(three.point(int(2)))) is True
    assert ask(image == component(three.point(int(1)))) is False
    assert ask(component.is_monomorphism()) is True

    lifted = extension.on_morphism(triangle.generator("1->2"))
    assert lifted in Mor(Sets())(extension.on_object(triangle(int(1))), extension.on_object(triangle(int(2))))
    assert ask(lifted.is_monomorphism()) is True
    assert ask(lifted(image) == lifted(component(three.point(int(1))))) is False
    composite = extension.on_morphism(triangle.generator("1->2") * triangle.generator("0->1"))
    assert ask(composite == lifted * extension.on_morphism(triangle.generator("0->1"))) is True
    assert ask(extension.on_morphism(triangle.generator("0->1")) * unit.component(arrow(int(0))) == component * successor) is True


def test_the_right_kan_extension_retains_its_counit() -> None:
    arrow, triangle = Cat().Simplex(int(1)), Cat().Simplex(int(2))
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    inclusion = _path_functor(arrow, triangle, lambda label: label)
    diagram = _arrow_diagram(two, three, successor)

    extension = right_kan_extension(inclusion, diagram)
    assert ask(extension.on_object(triangle(int(2))).cardinality() == int(1)) is True
    assert ask(extension.on_object(triangle(int(0))).cardinality() == int(2)) is True
    counit = right_kan_counit(inclusion, diagram)
    assert counit in Mor(Fun(arrow, Sets()))
    assert counit.codomain() is diagram
    assert counit.domain().on_object(arrow(int(0))) is extension.on_object(inclusion.on_object(arrow(int(0))))
    component = counit.component(arrow(int(0)))
    assert component.codomain() is two
    assert ask(component.is_isomorphism()) is True


def test_limits_in_a_functor_category_are_computed_pointwise() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    constant = Mor(Sets())(two, three)(lambda datum: int(0))
    arrow = Cat().Simplex(int(1))
    squares = Fun(arrow, Sets())
    index = Discrete(two)
    diagram = Fun(index, squares).from_object_rule(lambda vertex: successor if ask(vertex.point() == two.point(int(0))) is True else constant)

    product = squares.Products()(diagram)
    apex = product
    assert apex in squares
    assert apex in Fun.Products()
    assert ask(apex.on_object(arrow(int(0))).cardinality() == int(4)) is True
    assert ask(apex.on_object(arrow(int(1))).cardinality() == int(9)) is True
    at_source = apex.on_object(arrow(int(0)))
    assert at_source in Sets().Products()
    assert at_source.product_projection(index(two.point(int(1)))).codomain() is two
    first = product.product_projection(int(0))
    assert first in Mor(squares)(apex, successor)
    assert first.component(arrow(int(1))).codomain() is three
    assert ask(first.component(arrow(int(1))) * apex.on_morphism(arrow.generator("0->1")) == successor * first.component(arrow(int(0)))) is True

    coproduct = squares.Coproducts()(diagram)
    assert ask(coproduct.on_object(arrow(int(1))).cardinality() == int(6)) is True
    assert coproduct.coproduct_injection(int(1)).component(arrow(int(0))).domain() is two
