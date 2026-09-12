"""The selected coequalizer in ``Ab`` is computed by ModulePresentationsForCAP.

The public objects and maps remain the owned ``sage-categories`` objects.  The
test inspects the private native-retention record only to establish that the
actual selected quotient and its nonidentity projection came from CAP rather
than the former Python/Sage relation-stacking implementation.
"""

from sage.libs.gap.libgap import libgap

from sage_categories.algebra import (
    abelian_homomorphism,
    coequalizer_mediator,
    coequalizer_projection,
    AbelianGroups,
    presented_abelian_group,
)
from sage_categories.algebra._presented_modules_cap import (
    presented_native_morphism,
    presented_native_object,
)
from sage_categories.algebra.abelian import _coordinates
from sage_categories.cat.monoidal import Cartesian
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.predicates import ask
from sage_categories.cat.structured_objects import AdditiveGroups
from sage_categories.sets.finite import Sets


def test_cap_computes_the_selected_nonidentity_coequalizer_and_owned_mediator() -> None:
    two = AdditiveAbelianGroup([2])
    four = AdditiveAbelianGroup([4])
    source = presented_abelian_group(two)
    target = presented_abelian_group(four)
    generator = four.gen(0)
    zero = abelian_homomorphism(source, target, lambda _value: four.zero())
    double = abelian_homomorphism(
        source,
        target,
        lambda value: int(value.vector()[0]) * 2 * generator,
    )

    projection = coequalizer_projection(zero, double)
    apex = projection.codomain()
    native_apex = presented_native_object(apex)
    native_projection = presented_native_morphism(projection)

    assert native_apex.value is apex
    assert native_projection.value is projection
    assert native_projection.source is target
    assert native_projection.target is apex
    abelian = AbelianGroups()
    assert projection in Mor(abelian)(target, apex)

    groups = AdditiveGroups(Cartesian(Sets()))
    monoids = groups.named_monoids()
    magmas = monoids.named_magmas()
    forgetful = magmas.to_carrier() * monoids.to_named_magmas() * groups.to_named_monoids() * abelian.subcategory_monomorphism()
    forgotten_projection = forgetful.on_morphism(projection)
    assert forgotten_projection.domain() is forgetful.on_object(target)
    assert forgotten_projection.codomain() is forgetful.on_object(apex)
    assert libgap.Range(native_projection.native) == native_apex.native
    assert int(libgap.NumberColumns(libgap.UnderlyingMatrix(native_apex.native))) == 1

    image = projection(target.point(generator))
    assert ask(image == apex.zero()) is False
    assert ask(image + image == apex.zero()) is True

    # A nonidentity map x |-> 2x kills the image of the doubled generator, so it
    # factors through the selected Z/2 coequalizer without constructing another group.
    coequalizing = abelian_homomorphism(target, target, lambda value: 2 * value)
    mediator = coequalizer_mediator(projection, coequalizing)
    assert mediator.domain() is apex
    assert mediator.codomain() is target
    assert mediator in Mor(abelian)(apex, target)
    forgotten_mediator = forgetful.on_morphism(mediator)
    assert forgotten_mediator.domain() is forgetful.on_object(apex)
    assert forgotten_mediator.codomain() is forgetful.on_object(target)
    assert ask(mediator * projection == coequalizing) is True


def test_cap_colift_crosses_a_non_diagonal_raw_quotient_to_its_public_smith_basis() -> None:
    cyclic_engine = AdditiveAbelianGroup([4])
    square_engine = AdditiveAbelianGroup([4, 4])
    cyclic = presented_abelian_group(cyclic_engine)
    square = presented_abelian_group(square_engine)
    cyclic_generator = cyclic_engine.gen(0)

    def square_element(left, right):
        return square_engine.linear_combination_of_smith_form_gens(
            vector(ZZ, [left, right])
        )

    zero = abelian_homomorphism(cyclic, square, lambda _value: square_engine.zero())
    diagonal = abelian_homomorphism(
        cyclic,
        square,
        lambda value: int(value.vector()[0]) * square_element(1, 1),
    )
    projection = coequalizer_projection(zero, diagonal)
    apex = projection.codomain()

    native_apex = presented_native_object(apex).native
    assert int(libgap.NumberColumns(libgap.UnderlyingMatrix(native_apex))) == 2
    assert _coordinates(apex).rank() == 1

    difference = abelian_homomorphism(
        square,
        cyclic,
        lambda value: (
            (int(value.vector()[0]) - int(value.vector()[1])) * cyclic_generator
        ),
    )
    mediator = coequalizer_mediator(projection, difference)
    native_mediator = presented_native_morphism(mediator)
    assert native_mediator.value is mediator
    assert native_mediator.source is apex
    assert native_mediator.target is cyclic
    assert ask(mediator * projection == difference) is True


test_cap_computes_the_selected_nonidentity_coequalizer_and_owned_mediator()
test_cap_colift_crosses_a_non_diagonal_raw_quotient_to_its_public_smith_basis()
