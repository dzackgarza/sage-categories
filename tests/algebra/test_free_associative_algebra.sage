"""Native free associative algebra and its unbounded underlying module."""

from sage_categories.algebra import (
    free_associative_coefficients,
    free_associative_element,
    free_associative_generator,
    free_associative_product,
    free_associative_substitution,
    free_associative_underlying_module,
    free_associative_underlying_morphism,
    integer_free_associative_algebra,
)


def test_native_free_algebra_has_all_words_and_noncommutative_multiplication() -> None:
    algebra = integer_free_associative_algebra(("x", "y"))
    x = free_associative_generator(algebra, 0)
    y = free_associative_generator(algebra, 1)

    xy = free_associative_product(algebra, x, y)
    yx = free_associative_product(algebra, y, x)
    assert xy != yx
    assert xy == free_associative_element(algebra, {(0, 1): 1})
    assert yx == free_associative_element(algebra, {(1, 0): 1})

    long_word = tuple(position % 2 for position in range(101))
    long_element = free_associative_element(algebra, {long_word: 3})
    assert free_associative_coefficients(algebra, long_element) == {long_word: 3}


def test_native_substitution_commutes_with_the_underlying_module_functor() -> None:
    algebra = integer_free_associative_algebra(("x", "y"))
    module = free_associative_underlying_module(algebra)
    x = free_associative_generator(algebra, 0)
    y = free_associative_generator(algebra, 1)
    endomorphism = free_associative_substitution(algebra, (x + y, y))
    underlying = free_associative_underlying_morphism(endomorphism)
    assert underlying.domain() is module and underlying.codomain() is module

    xy = free_associative_product(algebra, x, y)
    image = underlying(xy)
    expected = free_associative_element(algebra, {(0, 1): 1, (1, 1): 1})
    assert image.parent() is module
    assert image == expected
    assert free_associative_coefficients(algebra, image) == {(0, 1): 1, (1, 1): 1}


test_native_free_algebra_has_all_words_and_noncommutative_multiplication()
test_native_substitution_commutes_with_the_underlying_module_functor()
