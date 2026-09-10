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
    presented_abelian_group,
)
from sage_categories.algebra._presented_modules_cap import (
    presented_native_morphism,
    presented_native_object,
)
from sage_categories.cat.predicates import ask


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
    assert libgap.Range(native_projection.native) == native_apex.native
    assert int(libgap.NumberColumns(libgap.UnderlyingMatrix(native_apex.native))) == 1

    image = projection(target.point(generator))
    assert ask(image == apex.zero()) is False
    assert ask(image + image == apex.zero()) is True

    plane_engine = AdditiveAbelianGroup([2, 2])
    plane = presented_abelian_group(plane_engine)
    corner = plane_engine.gen(0)
    coequalizing = abelian_homomorphism(
        target,
        plane,
        lambda value: int(value.vector()[0]) * corner,
    )
    mediator = coequalizer_mediator(projection, coequalizing)
    assert mediator.domain() is apex
    assert mediator.codomain() is plane
    assert ask(mediator * projection == coequalizing) is True


test_cap_computes_the_selected_nonidentity_coequalizer_and_owned_mediator()
