"""The owned binary biproduct in ``Ab`` retains CAP's selected direct sum privately."""

from sage.libs.gap.libgap import libgap

from sage_categories.algebra import AbelianGroups, abelian_homomorphism, presented_abelian_group
from sage_categories.algebra._presented_modules_cap import (
    presented_native_morphism,
    presented_native_object,
)
from sage_categories.cat.cones import cone, cones, cocone, cocones
from sage_categories.cat.diagrams import from_sequence, sequence_position
from sage_categories.cat.predicates import ask


def test_cap_direct_sum_preserves_the_owned_product_carrier_and_universal_maps() -> None:
    two_engine = AdditiveAbelianGroup([2])
    four_engine = AdditiveAbelianGroup([4])
    two = presented_abelian_group(two_engine)
    four = presented_abelian_group(four_engine)
    abelian = AbelianGroups()
    biproduct = abelian.biproduct(two, four)
    diagram = from_sequence(abelian, (two, four))
    shape = diagram.domain()
    product = abelian.Limits(shape).universal_data(diagram)
    coproduct = abelian.Colimits(shape).universal_data(diagram)
    assert product.apex() is biproduct
    assert coproduct.apex() is biproduct

    assert biproduct.point((two_engine.gen(0), four_engine.gen(0))).datum() == (
        two_engine.gen(0),
        four_engine.gen(0),
    )
    native = presented_native_object(biproduct)
    assert native.value is biproduct
    assert int(libgap.NumberColumns(libgap.UnderlyingMatrix(native.native))) == 2

    first_projection = product.leg(0)
    second_projection = product.leg(1)
    first_inclusion = coproduct.leg(0)
    second_inclusion = coproduct.leg(1)
    for arrow in (
        first_projection,
        second_projection,
        first_inclusion,
        second_inclusion,
    ):
        assert presented_native_morphism(arrow).value is arrow

    source_engine = AdditiveAbelianGroup([4])
    source = presented_abelian_group(source_engine)
    source_generator = source_engine.gen(0)
    to_two = abelian_homomorphism(
        source,
        two,
        lambda value: int(value.vector()[0]) * two_engine.gen(0),
    )
    to_four = abelian_homomorphism(
        source,
        four,
        lambda value: int(value.vector()[0]) * four_engine.gen(0),
    )
    product_legs = (to_two, to_four)
    paired = product.lift(
        cones(diagram)(
            cone(
                diagram,
                source,
                lambda vertex: product_legs[sequence_position(vertex)],
            )
        )
    )
    assert presented_native_morphism(paired).value is paired
    point = source.point(source_generator)
    assert ask(first_projection * paired == to_two) is True
    assert ask(second_projection * paired == to_four) is True

    target_engine = AdditiveAbelianGroup([4])
    target = presented_abelian_group(target_engine)
    from_two = abelian_homomorphism(
        two,
        target,
        lambda value: 2 * int(value.vector()[0]) * target_engine.gen(0),
    )
    from_four = abelian_homomorphism(
        four,
        target,
        lambda value: int(value.vector()[0]) * target_engine.gen(0),
    )
    coproduct_legs = (from_two, from_four)
    copaired = coproduct.lift(
        cocones(diagram)(
            cocone(
                diagram,
                target,
                lambda vertex: coproduct_legs[sequence_position(vertex)],
            )
        )
    )
    assert presented_native_morphism(copaired).value is copaired
    assert ask(copaired * first_inclusion == from_two) is True
    assert ask(copaired * second_inclusion == from_four) is True
    assert paired(point).parent() is biproduct


test_cap_direct_sum_preserves_the_owned_product_carrier_and_universal_maps()
