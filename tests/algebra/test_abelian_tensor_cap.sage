"""Finite presented tensors in ``Ab`` use ModulePresentationsForCAP on objects and maps."""

from sage.libs.gap.libgap import libgap

from sage_categories.algebra import (
    AbelianTensor,
    abelian_homomorphism,
    presented_abelian_group,
    simple_tensor,
)
from sage_categories.algebra._presented_modules_cap import (
    presented_native_morphism,
    presented_native_object,
)
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


test_cap_computes_finite_presented_tensor_object_and_nonidentity_tensor_map()
