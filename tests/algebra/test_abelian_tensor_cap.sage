"""Finite presented tensors in ``Ab`` use ModulePresentationsForCAP on objects and maps."""

from sage.libs.gap.libgap import libgap

from sage_categories.algebra import (
    AbelianTensor,
    abelian_homomorphism,
    coequalizer_projection,
    presented_abelian_group,
    simple_tensor,
    tensor_mediator,
)
from sage_categories.algebra._presented_modules_cap import (
    presented_native_morphism,
    presented_native_object,
)
from sage_categories.algebra.abelian import _coordinates
from sage_categories.cat.monoidal import tensor_morphism, tensor_object
from sage_categories.cat.predicates import ask


def test_cap_computes_finite_presented_tensor_object_and_nonidentity_tensor_map() -> None:
    four_engine = AdditiveAbelianGroup([4])
    six_engine = AdditiveAbelianGroup([6])
    four = presented_abelian_group(four_engine)
    six = presented_abelian_group(six_engine)

    monoidal = AbelianTensor()
    tensor_functor = monoidal.tensor()
    product = tensor_object(tensor_functor, four, six)
    native_tensor = presented_native_object(product)
    assert native_tensor.value is product
    assert int(libgap.NumberColumns(libgap.UnderlyingMatrix(native_tensor.native))) == 1

    four_generator = four_engine.gen(0)
    six_generator = six_engine.gen(0)
    generator_tensor = simple_tensor(four, six, four_generator, six_generator)
    assert generator_tensor.parent() is product
    assert ask(generator_tensor == product.zero()) is False
    assert ask(generator_tensor + generator_tensor == product.zero()) is True

    doubling = abelian_homomorphism(
        four,
        four,
        lambda value: 2 * int(value.vector()[0]) * four_generator,
    )
    identity = abelian_homomorphism(six, six, lambda value: value)
    induced = tensor_morphism(tensor_functor, doubling, identity)
    native_induced = presented_native_morphism(induced)
    assert native_induced.value is induced
    assert native_induced.source is product
    assert native_induced.target is product
    assert ask(induced(generator_tensor) == product.zero()) is True

    triples = monoidal.associator().domain().domain()
    associator = monoidal.associator().component(triples((four, six, four)))
    left_unitor = monoidal.left_unitor().component(four)
    right_unitor = monoidal.right_unitor().component(six)
    for comparison in (associator, left_unitor, right_unitor):
        for arrow in (comparison, comparison.inverse()):
            native_arrow = presented_native_morphism(arrow)
            assert native_arrow.value is arrow
            assert bool(
                libgap.IsIdenticalObj(
                    libgap.Source(native_arrow.native),
                    presented_native_object(arrow.domain()).native,
                )
            )
            assert bool(
                libgap.IsIdenticalObj(
                    libgap.Range(native_arrow.native),
                    presented_native_object(arrow.codomain()).native,
                )
            )


def test_simple_tensor_and_mediator_cross_a_cap_quotient_raw_basis() -> None:
    cyclic_engine = AdditiveAbelianGroup([4])
    square_engine = AdditiveAbelianGroup([4, 4])
    cyclic = presented_abelian_group(cyclic_engine)
    square = presented_abelian_group(square_engine)

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
    quotient = projection.codomain()
    two_engine = AdditiveAbelianGroup([2])
    two = presented_abelian_group(two_engine)
    tensor_functor = AbelianTensor().tensor()
    product = tensor_object(tensor_functor, quotient, two)

    quotient_generator = projection(square.point(square_element(1, 0)))
    assert quotient_generator.parent() is quotient
    generator = simple_tensor(quotient, two, quotient_generator.datum(), two_engine.gen(0))
    assert generator.parent() is product

    target_engine = AdditiveAbelianGroup([2])
    target = presented_abelian_group(target_engine)
    target_generator = target_engine.gen(0)
    mediator = tensor_mediator(
        quotient,
        two,
        target,
        lambda left, right: (
            int(_coordinates(quotient).coordinates(left)[0])
            * int(right.vector()[0])
            * target_generator
        ),
    )
    assert presented_native_morphism(mediator).value is mediator
    assert ask(mediator(generator) == target.point(target_generator)) is True


test_cap_computes_finite_presented_tensor_object_and_nonidentity_tensor_map()
test_simple_tensor_and_mediator_cross_a_cap_quotient_raw_basis()
