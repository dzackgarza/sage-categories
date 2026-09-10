"""Native free associative algebras as monoid objects in relative tensor modules."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from sympy import false, true

from sage_categories.algebra.abelian import (
    AbelianBimoduleTensor,
    AbelianTensor,
    balanced_tensor,
    indexed_free_abelian_injection,
    relative_tensor,
    relative_tensor_mediator,
)
from sage_categories.algebra.indexed_modules import (
    indexed_free_integer_coefficients,
    indexed_free_integer_element,
    indexed_free_integer_homomorphism,
    indexed_free_integer_module,
    integer_scalar_monoid,
)
from sage_categories.cat.bimodules import Bimodules
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.monoidal import tensor_object
from sage_categories.cat.native import NativeObjectRealizations
from sage_categories.cat.structured_objects import Magmas, Monoids
from sage_categories.engines import free_algebras
from sage_categories.sets.finite import Sets

type Word = tuple[int, ...]


@dataclass(frozen=True, eq=False, slots=True)
class IntegerFreeAssociativeConstruction:
    """Owned construction data for ``ZZ<x_0,...,x_n>``."""

    names: tuple[str, ...]
    word_module: CategoryOfCategories.ElementType


_objects: NativeObjectRealizations[object, IntegerFreeAssociativeConstruction] = (
    NativeObjectRealizations()
)


def _word_set(names: tuple[str, ...]):
    size = len(names)

    def is_word(value):
        if not isinstance(value, tuple):
            return false
        if not all(isinstance(position, int) for position in value):
            return false
        return true if all(0 <= position < size for position in value) else false

    return Sets.from_membership(is_word)


def _record(algebra):
    return _objects.realization(algebra)


def _source_module_point(record, terms: Mapping[Word, int]):
    return indexed_free_integer_element(record.construction.word_module, terms)


def _terms(record, datum) -> dict[Word, int]:
    point = record.construction.word_module.point(datum)
    return indexed_free_integer_coefficients(record.construction.word_module, point)


def _datum(record, terms: Mapping[Word, int]):
    return _source_module_point(record, terms).datum()


def integer_free_associative_algebra(
    names: Sequence[str] = ("x", "y"),
):
    r"""Return the native free associative algebra ``ZZ<names>`` as a monoid object.

    The carrier is the free ``ZZ``-module on the owned set of *all* finite
    words in the supplied alphabet.  Multiplication is descended through the
    relative tensor product of ``(ZZ,ZZ)``-bimodules and evaluated only by
    Sage's native ``FreeAlgebra``.
    """
    names = tuple(str(name) for name in names)
    if not names:
        raise ValueError("this consumer requires at least one free generator")
    native = free_algebras.integer_free_algebra(names)
    words = _word_set(names)
    word_module = indexed_free_integer_module(words)
    scalars = integer_scalar_monoid()
    absolute_tensor = AbelianTensor()
    bimodules = Bimodules(scalars, scalars, absolute_tensor)
    carrier = bimodules.left_modules().forgetful().on_object(word_module)
    left_action = word_module.action()
    right_action = absolute_tensor.right_unitor().component(carrier)
    bimodule = bimodules(left_action, right_action)
    structure = AbelianBimoduleTensor(scalars)
    projection = relative_tensor(bimodule.right_action(), bimodule.left_action())

    def multiply(left, right):
        record_terms_left = indexed_free_integer_coefficients(
            word_module, word_module.point(left)
        )
        record_terms_right = indexed_free_integer_coefficients(
            word_module, word_module.point(right)
        )
        terms = free_algebras.multiply(native, record_terms_left, record_terms_right)
        return indexed_free_integer_element(word_module, terms).datum()

    underlying_multiplication = relative_tensor_mediator(
        projection,
        carrier,
        multiply,
    )
    tensor_square = tensor_object(structure.tensor(), bimodule, bimodule)
    multiplication = bimodules.homomorphism(
        tensor_square,
        bimodule,
        underlying_multiplication,
    )
    additive_unit = indexed_free_abelian_injection(carrier, ())
    unit = bimodules.homomorphism(structure.unit(), bimodule, additive_unit)
    monoids = Monoids(structure)
    algebra = monoids(multiplication, unit)
    _objects.retain(
        monoids,
        algebra,
        native,
        IntegerFreeAssociativeConstruction(names, word_module),
    )
    return algebra


def free_associative_underlying_module(algebra):
    """Return the actual left ``ZZ``-module obtained from the algebra forgetful chain."""
    return _underlying_module_functor(algebra).on_object(algebra)


def _underlying_module_functor(algebra):
    record = _record(algebra)
    monoids = record.owner
    structure = monoids.monoidal_structure()
    bimodules = structure.underlying_category()
    return (
        bimodules.to_left()
        * Magmas(structure).forgetful()
        * monoids.to_magmas()
    )


def free_associative_element(algebra, terms: Mapping[Word, int]):
    """Return the underlying-module element with the supplied finite word coefficients."""
    record = _record(algebra)
    source_point = _source_module_point(record, terms)
    return free_associative_underlying_module(algebra).point(source_point.datum())


def free_associative_generator(algebra, position: int):
    """Return generator ``x_position`` as a point of the genuine underlying module."""
    record = _record(algebra)
    terms = free_algebras.generator(record.native, int(position))
    return free_associative_element(algebra, terms)


def free_associative_coefficients(algebra, element) -> dict[Word, int]:
    """Return the finite word-basis coefficient map of an underlying element."""
    record = _record(algebra)
    module = free_associative_underlying_module(algebra)
    if element.parent() is not module:
        raise ValueError("coefficients are read on the algebra's underlying module")
    source_point = record.construction.word_module.point(element.datum())
    return indexed_free_integer_coefficients(record.construction.word_module, source_point)


def free_associative_product(algebra, left, right):
    """Multiply two elements through the algebra's retained multiplication morphism."""
    module = free_associative_underlying_module(algebra)
    if left.parent() is not module or right.parent() is not module:
        raise ValueError("free-algebra multiplication takes elements of its underlying module")
    record = _record(algebra)
    monoids = record.owner
    structure = monoids.monoidal_structure()
    magma = monoids.to_magmas().on_object(algebra)
    bimodules = structure.underlying_category()
    bimodule = Magmas(structure).forgetful().on_object(magma)
    projection = relative_tensor(bimodule.right_action(), bimodule.left_action())
    balanced = balanced_tensor(projection, left.datum(), right.datum())
    operation = bimodules.forgetful().on_morphism(algebra.operation())
    return module.point(operation(balanced).datum())


def free_associative_substitution(algebra, images: Sequence[CategoryOfCategories.ElementType]):
    r"""Return the algebra endomorphism with the supplied generator images.

    Sage evaluates every basis word at the selected images.  The resulting
    additive map is lifted through the actual bimodule and monoid morphism
    constructors, so forgetting this arrow gives the same map on the genuine
    underlying module; no degree bound appears.
    """
    record = _record(algebra)
    module = free_associative_underlying_module(algebra)
    if len(images) != len(record.construction.names):
        raise ValueError("one image is required for every free generator")
    if any(image.parent() is not module for image in images):
        raise ValueError("generator images belong to the algebra's underlying module")
    image_terms = tuple(_terms(record, image.datum()) for image in images)
    source_module = record.construction.word_module

    def basis_image(word: Word):
        terms = free_algebras.substitute(record.native, {word: 1}, image_terms)
        return source_module.point(_datum(record, terms))

    source_linear = indexed_free_integer_homomorphism(
        source_module,
        source_module,
        basis_image,
    )
    monoids = record.owner
    structure = monoids.monoidal_structure()
    bimodules = structure.underlying_category()
    carrier_map = bimodules.left_modules().forgetful().on_morphism(source_linear)
    magma = monoids.to_magmas().on_object(algebra)
    bimodule = Magmas(structure).forgetful().on_object(magma)
    bimodule_map = bimodules.homomorphism(bimodule, bimodule, carrier_map)
    return monoids.homomorphism(algebra, algebra, bimodule_map)


def free_associative_underlying_morphism(algebra_morphism):
    """Forget a retained free-algebra morphism to its actual left-module map."""
    return _underlying_module_functor(algebra_morphism.domain()).on_morphism(
        algebra_morphism
    )


__all__ = [
    "IntegerFreeAssociativeConstruction",
    "free_associative_coefficients",
    "free_associative_element",
    "free_associative_generator",
    "free_associative_product",
    "free_associative_substitution",
    "free_associative_underlying_module",
    "free_associative_underlying_morphism",
    "integer_free_associative_algebra",
]
