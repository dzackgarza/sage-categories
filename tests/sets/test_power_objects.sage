"""Power objects ``2 ** X``, the subset algebra of chosen subsets, and the subset poset.

Oracles: ``2 ** X`` is the function set into ``2 = [1]`` and ``#(2 ** X) = 2 ** #X``
(Mathlib ``Cardinal.mk_set``: ``2 ** 3 = 8``); the characteristic function of a subset
takes ``1`` exactly on its members (nLab "subobject classifier" in ``Set``; Mathlib
``Set.mem_iff_boolIndicator``); the definitions of union, intersection, difference,
symmetric difference, and complement on the divisibility specimen ``{1, 2, 3, 6}`` and the
evens ``{0, 2, 4, 6}`` inside ``[6] = {0, ..., 6}`` by direct computation: union
``{0, 1, 2, 3, 4, 6}``, intersection ``{2, 6}``, difference ``{1, 3}``, symmetric
difference ``{0, 1, 3, 4}``, complement ``{0, 4, 5}``; the direct image of ``{1, 2, 3, 6}``
under ``d |-> d mod 3`` is ``{0, 1, 2}`` and the preimage of ``{1}`` is ``{1, 4}``
(Mathlib ``Set.mem_image``, ``Set.mem_preimage``); the power set is a poset under
containment (nLab "power set"), with ``{} <= {a} <= {a, b}`` and ``{a}``, ``{b}``
incomparable.
"""

import pytest

from sage_categories.all import *


def _six():
    return Sets().Simplex(int(6))


def _divisors():
    return _six().subset_from(lambda datum: datum in (int(1), int(2), int(3), int(6)))


def _evens():
    return _six().subset_from(lambda datum: datum % int(2) == int(0))


def test_the_power_object_is_the_function_set_into_two_with_the_exact_cardinality() -> None:
    two, three, six = Sets().Simplex(int(1)), Sets().Simplex(int(2)), _six()
    power = two ** three

    assert power is Sets().exponential(three, two)
    assert power is Sets().PowerObjects()(three)
    assert power in Sets().PowerObjects()
    assert power in Sets()
    assert power.base_set() is three
    assert ask(power.cardinality() == int(8))
    assert ask((two ** six).cardinality() == int(128))
    assert (two ** six).base_set() is six
    assert (two ** ZZ).cardinality() is continuum
    assert (three ** three) not in Sets().PowerObjects()

    divisors = _divisors()
    named = Sets().name_of(divisors.characteristic_morphism())
    assert named in two ** six
    assert named.parent() is two ** six


def test_characteristic_morphisms_and_subsets_from_them_are_mutually_inverse() -> None:
    two, six = Sets().Simplex(int(1)), _six()
    power = two ** six
    divisors = _divisors()
    characteristic = divisors.characteristic_morphism()

    assert characteristic in Mor(Sets())(six, two)
    assert Sets().ChosenSubsets().characteristic_morphism_of(divisors) is characteristic
    assert ask(characteristic(six.point(int(2))) == two.point(int(1)))
    assert ask(characteristic(six.point(int(4))) == two.point(int(0)))
    assert ask(characteristic(six.point(int(6))) == two.point(int(1)))

    recovered = power.from_characteristic_morphism(characteristic)
    assert Sets().PowerObjects().subset_of_characteristic_morphism(power, characteristic) is recovered
    assert recovered in Sets().ChosenSubsets()
    assert recovered.underlying_set() is six
    assert ask(recovered.cardinality() == int(4))
    assert six.point(int(3)) in recovered
    assert six.point(int(4)) not in recovered
    assert ask(recovered <= divisors)
    assert ask(divisors <= recovered)
    assert ask(recovered.characteristic_morphism() == characteristic)

    predicate_subset = power.from_predicate(lambda datum: datum > int(4))
    assert ask(predicate_subset.cardinality() == int(2))
    assert predicate_subset.underlying_set() is six
    assert ask(power.top().cardinality() == int(7))
    assert ask(power.bottom().cardinality() == int(0))
    assert Sets().PowerObjects().extreme_subset(power, True) is power.top()
    assert ask(divisors <= power.top())
    assert ask(power.bottom() <= divisors)
    assert not ask(power.top() <= divisors)


def test_the_subset_algebra_on_the_divisibility_specimen() -> None:
    six = _six()
    divisors, evens = _divisors(), _evens()

    union = divisors.union(evens)
    assert union in Sets().ChosenSubsets()
    assert union.underlying_set() is six
    assert ask(union.cardinality() == int(6))
    assert six.point(int(5)) not in union
    assert six.point(int(0)) in union
    assert ask((divisors | evens).cardinality() == int(6))
    assert ask(divisors <= union)
    assert ask(evens <= union)
    assert not ask(union <= divisors)

    intersection = divisors.intersection(evens)
    assert ask(intersection.cardinality() == int(2))
    assert six.point(int(2)) in intersection and six.point(int(6)) in intersection
    assert six.point(int(3)) not in intersection
    assert ask((divisors & evens).cardinality() == int(2))
    assert ask(intersection <= divisors)
    assert ask(intersection <= evens)

    difference = divisors.difference(evens)
    assert ask(difference.cardinality() == int(2))
    assert six.point(int(1)) in difference and six.point(int(3)) in difference
    assert six.point(int(2)) not in difference

    symmetric = divisors.symmetric_difference(evens)
    assert ask(symmetric.cardinality() == int(4))
    assert six.point(int(4)) in symmetric and six.point(int(1)) in symmetric
    assert six.point(int(6)) not in symmetric

    complement = divisors.complement()
    assert ask(complement.cardinality() == int(3))
    assert six.point(int(5)) in complement
    assert six.point(int(6)) not in complement
    assert ask(complement.intersection(divisors).cardinality() == int(0))
    assert ask(complement.union(divisors).cardinality() == int(7))
    assert ask(divisors <= divisors)
    assert not ask(divisors <= evens)
    with pytest.raises(TypeError):
        bool(divisors <= evens)

    undecided = ZZ.subset_from(lambda datum: Unknown)
    assert ask(Primes <= undecided) is Unknown
    assert ask(Primes <= ZZ.subset_from(lambda datum: datum > int(1))) is Unknown
    with pytest.raises(AssertionError):
        divisors.union(Primes)


def test_direct_and_inverse_image_morphisms_act_on_names_of_characteristic_morphisms() -> None:
    two, three, six = Sets().Simplex(int(1)), Sets().Simplex(int(2)), _six()
    residue = Mor(Sets())(six, three)(lambda datum: datum % int(3))
    power, target = two ** six, two ** three
    divisors = _divisors()

    direct = power.direct_image_morphism(residue)
    assert direct in Mor(Sets())(power, target)
    assert Sets().PowerObjects().direct_image_morphism(power, residue) is direct
    image_name = direct(Sets().name_of(divisors.characteristic_morphism()))
    assert image_name in target
    image = target.subset_named_by(image_name)
    assert ask(image.cardinality() == int(3))
    assert three.point(int(0)) in image
    assert power.subset_named_by(Sets().name_of(divisors.characteristic_morphism())) is power.from_characteristic_morphism(divisors.characteristic_morphism())

    inverse = target.inverse_image_morphism(residue)
    assert inverse in Mor(Sets())(target, power)
    one = three.subset_from(lambda datum: datum == int(1))
    preimage = power.subset_named_by(inverse(Sets().name_of(one.characteristic_morphism())))
    assert ask(preimage.cardinality() == int(2))
    assert six.point(int(1)) in preimage and six.point(int(4)) in preimage
    assert six.point(int(2)) not in preimage


def test_the_subset_poset_orders_the_power_object_by_inclusion() -> None:
    letters = Sets().Finite()(("a", "b"))
    two = Sets().Simplex(int(1))
    poset = Posets().subset_poset(letters)
    power = two ** letters
    underlying = Posets().structure_functors()[int(0)]

    assert poset in Posets()
    assert underlying.on_object(poset) is power
    assert power.base_set() is letters
    assert ask(poset.cardinality() == int(4))

    empty, only_a, only_b, whole = (
        poset.element(Sets().name_of(subset.characteristic_morphism()))
        for subset in (power.bottom(), letters.subset_from(lambda datum: datum == "a"), letters.subset_from(lambda datum: datum == "b"), power.top())
    )
    assert ask(empty <= only_a)
    assert ask(only_a <= whole)
    assert ask(empty <= whole)
    assert not ask(only_a <= only_b)
    assert not ask(only_b <= only_a)
    assert not ask(whole <= only_a)
    assert ask(only_a <= only_a)
    assert ask(poset.is_total()) is Unknown
