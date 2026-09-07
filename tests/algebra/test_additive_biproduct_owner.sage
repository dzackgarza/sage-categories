"""A mixed free and torsion biproduct in Ab, with both universal maps and its forgetful images."""

from sage_categories.all import Fun, Mor, Sets, ask
from sage_categories.algebra import AbelianGroups, abelian_homomorphism, integer_group, presented_abelian_group
from sage_categories.cat.cones import cone, cones, cocone, cocones
from sage_categories.cat.diagrams import from_sequence, sequence_position


def test_mixed_biproduct_has_additive_universal_maps() -> None:
    abelian = AbelianGroups()
    integers = integer_group()
    engine = AdditiveAbelianGroup([4])
    cyclic = presented_abelian_group(engine)
    generator = engine.gen(0)
    biproduct = abelian.biproduct(integers, cyclic)
    diagram = from_sequence(abelian, (integers, cyclic))
    shape = diagram.domain()
    product = abelian.Limits(shape).universal_data(diagram)
    coproduct = abelian.Colimits(shape).universal_data(diagram)
    assert product.apex() is biproduct
    assert coproduct.apex() is biproduct
    first, second = product.leg(0), product.leg(1)
    include_first, include_second = coproduct.leg(0), coproduct.leg(1)
    assert ask(first * include_first == Mor(abelian)(integers, integers).one()) is True
    assert ask(second * include_second == Mor(abelian)(cyclic, cyclic).one()) is True
    assert ask(first * include_second == abelian.zero_morphism(cyclic, integers)) is True
    assert ask(second * include_first == abelian.zero_morphism(integers, cyclic)) is True

    double = abelian_homomorphism(integers, integers, lambda value: 2 * value)
    reduction = abelian_homomorphism(integers, cyclic, lambda value: value * generator)
    pairing_legs = (double, reduction)
    pairing = product.lift(cones(diagram)(cone(
        diagram, integers, lambda vertex: pairing_legs[sequence_position(vertex)],
    )))
    copairing_legs = (reduction, Mor(abelian)(cyclic, cyclic).one())
    copairing = coproduct.lift(cocones(diagram)(cocone(
        diagram, cyclic, lambda vertex: copairing_legs[sequence_position(vertex)],
    )))
    for index in (0, 1):
        assert ask(product.leg(index) * pairing == pairing_legs[index]) is True
        assert ask(copairing * coproduct.leg(index) == copairing_legs[index]) is True
    triple_reduction = abelian_homomorphism(integers, cyclic, lambda value: 3 * value * generator)
    assert ask(copairing * pairing == triple_reduction) is True
    assert pairing.base_category() is abelian
    assert copairing.base_category() is abelian

    forgetful = abelian.forgetful()
    assert forgetful in Fun(abelian, Sets)
    carrier = forgetful.on_object(integers)
    image = forgetful.on_morphism(reduction)
    assert image.domain() is carrier
    assert image.codomain() is forgetful.on_object(cyclic)
    assert image(carrier.point(3)) is image.codomain().point(3 * generator)
    assert ask(forgetful.on_morphism(first) * forgetful.on_morphism(pairing)
               == forgetful.on_morphism(double)) is True
    plain_product = Sets.Products()((Sets(("left", "right")), Sets(("up", "down"))))
    assert plain_product.product_projection(0)(plain_product.point(("left", "up"))).datum() == "left"


test_mixed_biproduct_has_additive_universal_maps()
