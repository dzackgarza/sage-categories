"""``Cardinal()`` as a skeletal presentation of ``Sets()``: representatives, cardinal morphisms, order as inhabitation, and the cardinality functor.

Oracles: ``#{0, ..., n - 1} = n`` (Mathlib ``Cardinal.mk_fin``); ``Mor(Cardinal())(kappa, lambda)``
is the discrete category on the functions between the representatives
(``specs/cardinality.md``, "Cardinal model"); a function ``A -> B`` exists exactly when
``A`` is empty or ``B`` is nonempty (Mathlib ``nonempty_fun``); ``kappa <= lambda`` is
the existence of an injection (Mathlib ``Cardinal.le_def``) and ``kappa = lambda`` of a
bijection (``Cardinal.eq``); ``2 ** aleph0 = aleph(1)`` under the continuum hypothesis,
which this package assumes by default (``specs/cardinality.md``, "The continuum
hypothesis"), so that hom category is inhabited and the one from ``aleph(2)`` is not;
the cardinality functor sends a bijection to the conjugate by the selected bijections
with the representatives (``specs/cardinality.md``, "Integration with ``Sets()``");
finite set-map equality is decided pointwise (``specs/sets.md``, "Equality").
"""

import pytest

from sage_categories.all import *


def _cardinals():
    return Cardinal()


def _representative_functor():
    (functor,) = Cardinal().structure_functors()
    return functor


def test_each_cardinal_selects_one_representative_set() -> None:
    cardinals, functor = _cardinals(), _representative_functor()
    three = cardinals(int(3))
    countable = cardinals.representative(aleph0)

    assert functor in Fun(cardinals, Sets()).FullyFaithful()
    assert functor.domain() is cardinals and functor.codomain() is Sets()
    assert cardinals.representative(three) is Sets().Simplex(int(2))
    assert functor.on_object(three) is Sets().Simplex(int(2))
    assert cardinals.representative(cardinals(int(0))) is Sets().Empty()
    assert functor.on_object(aleph0) is countable
    assert countable in Sets()
    assert countable.cardinality() is aleph0
    assert ask(countable.is_countable())
    assert not ask(countable.is_finite())
    assert three not in Sets()
    assert three in cardinals
    assert ask(cardinals.representative(continuum).is_uncountable())


def test_cardinal_morphisms_are_functions_between_representatives_and_compose_as_such() -> None:
    cardinals, functor = _cardinals(), _representative_functor()
    two, three, five = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(4))
    successor = Mor(Sets())(three, five)(lambda datum: datum + int(1))
    parity = Mor(Sets())(five, two)(lambda datum: datum % int(2))
    lift = Mor(cardinals)(cardinals(int(3)), cardinals(int(5)))(successor)
    collapse = Mor(cardinals)(cardinals(int(5)), cardinals(int(2)))(parity)

    assert lift in Mor(cardinals)(cardinals(int(3)), cardinals(int(5)))
    assert lift in Mor(cardinals)
    assert lift.domain() is cardinals(int(3)) and lift.codomain() is cardinals(int(5))
    assert functor.on_morphism(lift) is successor
    composite = collapse * lift
    assert composite in Mor(cardinals)(cardinals(int(3)), cardinals(int(2)))
    assert ask(functor.on_morphism(composite) == parity * successor)
    assert ask(functor.on_morphism(composite)(three.point(int(2))) == two.point(int(1)))
    with pytest.raises(AssertionError):
        Mor(cardinals)(cardinals(int(2)), cardinals(int(5)))(successor)

    identity = cardinals(int(3)).identity()
    assert identity in Mor(cardinals)(cardinals(int(3)), cardinals(int(3)))
    assert identity in Mor(cardinals).Automorphisms()
    assert functor.on_morphism(identity) is three.identity()
    assert ask(lift * identity == lift) is not False

    swap = Mor(cardinals)(cardinals(int(2)), cardinals(int(2))).Isomorphisms()(Mor(Sets())(two, two)(lambda datum: int(1) - datum))
    assert swap in Mor(cardinals).Isomorphisms()
    assert swap.inverse() in Mor(cardinals)(cardinals(int(2)), cardinals(int(2)))
    assert ask(functor.on_morphism(swap.inverse() * swap) == two.identity())
    assert swap.inverse().inverse() is swap


def test_inhabitation_of_cardinal_hom_categories_is_decided_by_cardinal_comparison() -> None:
    cardinals = _cardinals()
    zero, three, five = cardinals(int(0)), cardinals(int(3)), cardinals(int(5))
    aleph1 = cardinals.aleph(int(1))

    assert ask(Mor(cardinals)(three, five).is_inhabited())
    assert ask(Mor(cardinals)(five, three).is_inhabited())
    assert not ask(Mor(cardinals)(five, zero).is_inhabited())
    assert ask(Mor(cardinals)(five, zero).is_empty())
    assert ask(Mor(cardinals)(zero, five).is_inhabited())
    assert ask(Mor(cardinals)(zero, zero).is_inhabited())
    assert not ask(Mor(cardinals)(aleph0, zero).is_inhabited())

    assert ask(Mor(cardinals).Monomorphisms()(three, five).is_inhabited())
    assert not ask(Mor(cardinals).Monomorphisms()(five, three).is_inhabited())
    assert ask(Mor(cardinals).Monomorphisms()(five, three).is_empty())
    assert not ask(Mor(cardinals).Monomorphisms()(aleph0, three).is_inhabited())
    assert ask(Mor(cardinals).Monomorphisms()(three, aleph0).is_inhabited())
    assert ask(Mor(cardinals).Monomorphisms()(aleph1, continuum).is_inhabited())
    assert not ask(Mor(cardinals).Monomorphisms()(cardinals.aleph(int(2)), continuum).is_inhabited())
    assert not ask(Mor(cardinals).Isomorphisms()(three, five).is_inhabited())
    assert ask(Mor(cardinals).Isomorphisms()(three, three).is_inhabited())
    assert ask(Mor(cardinals).Isomorphisms()(aleph1, continuum).is_inhabited())
    assert ask(Mor(cardinals).Epimorphisms()(five, three).is_inhabited()) is Unknown


def test_cardinal_order_is_the_inhabitation_of_the_monomorphism_category() -> None:
    cardinals = _cardinals()
    three, five = cardinals(int(3)), cardinals(int(5))
    proposition = three <= five

    assert proposition.arguments()[int(0)] is Mor(cardinals).Monomorphisms()(three, five)
    assert ask(proposition)
    assert not ask(five <= three)
    assert ask(three <= int(3))
    assert ask(int(5) >= three)
    assert ask(aleph0 <= continuum)
    assert ask(cardinals.aleph(int(1)) <= continuum)
    assert ask(continuum <= cardinals.aleph(int(1)))
    assert not ask(cardinals.aleph(int(2)) <= continuum)
    assert ask(three < five)
    assert not ask(five < three)
    with pytest.raises(TypeError):
        bool(three <= five)


def test_the_cardinality_functor_sends_a_bijection_to_a_cardinal_isomorphism() -> None:
    cardinals, functor = _cardinals(), _representative_functor()
    counting = Sets().CardinalityFunctor()
    three, letters = Sets().Simplex(int(2)), Sets().Finite()(("a", "b", "c"))
    name = Mor(Sets())(three, letters).Isomorphisms()(lambda datum: "abc"[datum], lambda letter: "abc".index(letter))
    rotate = Mor(Sets())(three, letters).Isomorphisms()(lambda datum: "abc"[(datum + int(1)) % int(3)], lambda letter: ("abc".index(letter) - int(1)) % int(3))
    collapse = Mor(Sets())(three, Sets().Simplex(int(1)))(lambda datum: min(datum, int(1)))

    assert counting is Sets().CardinalityFunctor()
    assert counting in Fun(Sets().Core(), cardinals)
    assert counting.domain() is Sets().Core() and counting.codomain() is cardinals
    assert counting.on_object(letters) is cardinals(int(3))
    assert counting.on_object(three) is cardinals(int(3))
    assert counting.on_object(NN) is aleph0
    assert counting.on_object(RR) is continuum

    named = counting.on_morphism(name)
    assert named in Mor(cardinals)(cardinals(int(3)), cardinals(int(3))).Isomorphisms()
    assert ask(named.is_endomorphism())
    assert named in Mor(cardinals).Automorphisms()
    assert functor.on_morphism(named) in Mor(Sets())(three, three)
    assert ask(functor.on_morphism(named) == three.identity())
    rotated = counting.on_morphism(rotate)
    assert ask(functor.on_morphism(rotated)(three.point(int(0))) == three.point(int(1)))
    assert ask(functor.on_morphism(rotated)(three.point(int(2))) == three.point(int(0)))
    assert not ask(functor.on_morphism(rotated) == three.identity())
    assert ask(functor.on_morphism(rotated.inverse() * rotated) == three.identity())

    shift = counting.on_morphism(Mor(Sets())(ZZ, ZZ).Isomorphisms()(lambda datum: datum + int(1), lambda datum: datum - int(1)))
    assert shift in Mor(cardinals)(aleph0, aleph0).Isomorphisms()
    with pytest.raises(AssertionError):
        counting.on_morphism(collapse)
    with pytest.raises(AssertionError):
        counting.on_object(Sets()(lambda datum: type(datum) is int))
