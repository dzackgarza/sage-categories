"""Declared implementations and comma constructions through their public consumers."""

from __future__ import annotations

from sage_categories.all import Cat, Category, Fun, Mor, ask
from sage_categories.cat.adjunctions import Adjunctions, Equivalences
from sage_categories.cat.canonical import FinitePresentedCategory
from sage_categories.cat.cones import cone, cones
from sage_categories.cat.dual_functor_categories import dual_functor_category_equivalence


def interval_arrow(category: FinitePresentedCategory, first: int, last: int) -> FinitePresentedCategory.MorphismType:
    return Mor(category)(category(first), category(last))(
        tuple(f"{index}->{index + 1}" for index in range(first, last))
    )


def test_declared_implementation_initializes_its_mathematical_parameters() -> None:
    residues = Cat().declare("ResiduesForConstruction")

    class Residues(Category):
        class ObjectType:
            def __init__(self, data: int) -> None:
                self._residue = data % self.category().modulus()

            def residue(self) -> int:
                return self._residue

        class ElementType:
            pass

        class MorphismType:
            pass

        def __init__(self) -> None:
            self._modulus = 7

        def modulus(self) -> int:
            return self._modulus

        def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
            return (Fun(residues, residues).one(),)

        def __call__(self, data: int) -> Residues.ObjectType:
            return self.ObjectType(data)

    Cat().implement(Residues)
    assert residues(10).residue() == 3
    assert residues(19).residue() == 5
    assert residues(10) is residues(10)


def test_comma_objects_squares_and_composition() -> None:
    source, target = Cat().Simplex(2), Cat().Simplex(3)
    inclusion = Fun(source, target)(
        lambda value: target(source.label(value)),
        lambda arrow: interval_arrow(target, source.label(arrow.domain()), source.label(arrow.codomain())),
    )
    shifted = Fun(source, target)(
        lambda value: target(source.label(value) + 1),
        lambda arrow: interval_arrow(target, source.label(arrow.domain()) + 1, source.label(arrow.codomain()) + 1),
    )
    comma = Cat().Comma(inclusion, shifted)
    objects = tuple(comma.from_arrow(source(index), source(index), interval_arrow(target, index, index + 1)) for index in range(3))
    first = Mor(comma)(objects[0], objects[1])(source.generator("0->1"), source.generator("0->1"))
    second = Mor(comma)(objects[1], objects[2])(source.generator("1->2"), source.generator("1->2"))
    composite = second * first

    assert objects[1].first() is source(1)
    assert objects[1].second() is source(1)
    assert objects[1].arrow() is target.generator("1->2")
    assert comma.from_arrow(source(1), source(1), target.generator("1->2")) is objects[1]
    assert ask(composite.first() == interval_arrow(source, 0, 2)) is True
    assert ask(composite.second() == interval_arrow(source, 0, 2)) is True
    assert ask(shifted.on_morphism(composite.second()) * objects[0].arrow() == objects[2].arrow() * inclusion.on_morphism(composite.first())) is True

    presentation = Cat().Pullbacks().presentation(comma)
    competing = Fun(source, comma)(
        lambda value: objects[source.label(value)],
        lambda arrow: Mor(comma)(objects[source.label(arrow.domain())], objects[source.label(arrow.codomain())])(arrow, arrow),
    )
    candidate = cone(presentation.diagram(), source, lambda vertex: presentation.leg(vertex) * competing)
    induced = presentation.lift(cones(presentation.diagram())(candidate))
    assert ask(induced.on_object(source(1)).arrow() == target.generator("1->2")) is True
    assert ask(induced.on_morphism(interval_arrow(source, 0, 2)).first() == interval_arrow(source, 0, 2)) is True


def test_total_cones_inherit_comma_maps_and_universal_mediators() -> None:
    shape, category = Cat().Simplex(1), Cat().Simplex(3)
    diagrams = Fun(shape, category)
    first_diagram = category.arrow_functor(category.generator("1->2"))
    second_diagram = category.arrow_functor(category.generator("2->3"))
    third_diagram = diagrams.constant(category(3))
    first_cone = cones(first_diagram)(cone(first_diagram, category(0), lambda vertex: interval_arrow(category, 0, shape.label(vertex) + 1)))
    second_cone = cones(second_diagram)(cone(second_diagram, category(1), lambda vertex: interval_arrow(category, 1, shape.label(vertex) + 2)))
    third_cone = cones(third_diagram)(cone(third_diagram, category(2), lambda vertex: category.generator("2->3")))
    eta = Mor(diagrams)(first_diagram, second_diagram)(lambda vertex: interval_arrow(category, shape.label(vertex) + 1, shape.label(vertex) + 2))
    theta = Mor(diagrams)(second_diagram, third_diagram)(lambda vertex: interval_arrow(category, shape.label(vertex) + 2, 3))
    total = diagrams.TotalCones()
    first, second, third = total(first_cone), total(second_cone), total(third_cone)
    forward = Mor(total)(first, second)(category.generator("0->1"), eta)
    onward = Mor(total)(second, third)(category.generator("1->2"), theta)
    composite = onward * forward

    assert first.presentation() is first_cone
    assert total(first_cone) is first
    assert ask(composite.apex_morphism() == interval_arrow(category, 0, 2)) is True
    assert ask(composite.diagram_transformation().component(shape(0)) == interval_arrow(category, 1, 3)) is True
    assert ask(total.apex_functor().on_morphism(composite) == interval_arrow(category, 0, 2)) is True
    assert ask(total.diagram_projection().on_morphism(composite).component(shape(1)) == category.generator("2->3")) is True

    presentation = Cat().Pullbacks().presentation(total)
    endpoints = (first, third)
    competing = Fun(shape, total)(
        lambda value: endpoints[shape.label(value)],
        lambda arrow: Mor(total)(endpoints[shape.label(arrow.domain())], endpoints[shape.label(arrow.domain())]).one()
        if arrow.domain() is arrow.codomain() else composite,
    )
    candidate = cone(presentation.diagram(), shape, lambda vertex: presentation.leg(vertex) * competing)
    induced = presentation.lift(cones(presentation.diagram())(candidate))
    assert induced.on_object(shape(1)).presentation() is third_cone
    assert ask(induced.on_morphism(shape.generator("0->1")).apex_morphism() == interval_arrow(category, 0, 2)) is True


def test_duality_retains_equivalence_data_and_transports_transformations() -> None:
    shape, category = Cat().Simplex(1), Cat().Simplex(3)
    diagrams = Fun(shape, category)
    source = category.arrow_functor(category.generator("1->2"))
    target = category.arrow_functor(category.generator("2->3"))
    eta = Mor(diagrams)(source, target)(lambda vertex: interval_arrow(category, shape.label(vertex) + 1, shape.label(vertex) + 2))
    equivalence = dual_functor_category_equivalence(shape, category)
    forward, inverse = equivalence.forward(), equivalence.inverse()
    selected = Equivalences(forward.domain(), forward.codomain())
    adjunctions = Adjunctions(forward, inverse)
    adjunction = adjunctions(equivalence.unit(), equivalence.counit())

    assert dual_functor_category_equivalence(shape, category) is equivalence
    assert selected(forward, inverse, equivalence.unit(), equivalence.counit()) is equivalence
    assert adjunctions(equivalence.unit(), equivalence.counit()) is adjunction
    assert ask(selected.is_inhabited()) is True
    assert ask(adjunctions.is_inhabited()) is True
    assert inverse.on_object(forward.on_object(source)) is source
    returned = inverse.on_morphism(forward.on_morphism(eta))
    assert ask(returned.component(shape(0)) == category.generator("1->2")) is True
    assert ask(returned.component(shape(1)) == category.generator("2->3")) is True
    assert dual_functor_category_equivalence(shape, Cat().Simplex(2)) is not equivalence


test_declared_implementation_initializes_its_mathematical_parameters()
test_comma_objects_squares_and_composition()
test_total_cones_inherit_comma_maps_and_universal_mediators()
test_duality_retains_equivalence_data_and_transports_transformations()
